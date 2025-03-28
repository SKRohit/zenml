#  Copyright (c) ZenML GmbH 2021. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

import os
import sys
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

import click
import kfp
import tfx.orchestration.pipeline as tfx_pipeline
import urllib3
from kubernetes import config

from zenml.constants import APP_NAME
from zenml.core.component_factory import orchestrator_store_factory
from zenml.core.repo import Repository
from zenml.enums import OrchestratorTypes
from zenml.integrations.kubeflow.orchestrators import local_deployment_utils
from zenml.integrations.kubeflow.orchestrators.kubeflow_dag_runner import (
    KubeflowDagRunner,
    KubeflowDagRunnerConfig,
)
from zenml.integrations.utils import get_requirements_for_module
from zenml.io import fileio
from zenml.logger import get_logger
from zenml.orchestrators.base_orchestrator import BaseOrchestrator

if TYPE_CHECKING:
    from zenml.pipelines.base_pipeline import BasePipeline

logger = get_logger(__name__)


@orchestrator_store_factory.register(OrchestratorTypes.kubeflow)
class KubeflowOrchestrator(BaseOrchestrator):
    """Orchestrator responsible for running pipelines using Kubeflow."""

    custom_docker_base_image_name: Optional[str] = None
    kubernetes_context: Optional[str] = None

    def get_docker_image_name(self, pipeline_name: str) -> str:
        """Returns the full docker image name including registry and tag."""

        base_image_name = f"zenml-kubeflow:{pipeline_name}"
        container_registry = Repository().get_active_stack().container_registry

        if container_registry:
            registry_uri = container_registry.uri.rstrip("/")
            return f"{registry_uri}/{base_image_name}"
        else:
            return base_image_name

    @property
    def root_directory(self) -> str:
        """Returns path to the root directory for all files concerning
        this orchestrator."""
        return os.path.join(
            click.get_app_dir(APP_NAME), "kubeflow", str(self.uuid)
        )

    @property
    def pipeline_directory(self) -> str:
        """Returns path to a directory in which the kubeflow pipeline files
        are stored."""
        return os.path.join(self.root_directory, "pipelines")

    def pre_run(self, pipeline: "BasePipeline", caller_filepath: str) -> None:
        """Builds a docker image for the current environment and uploads it to
        a container registry if configured.
        """
        from zenml.integrations.kubeflow.docker_utils import (
            build_docker_image,
            push_docker_image,
        )

        image_name = self.get_docker_image_name(pipeline.pipeline_name)

        repository_root = Repository().path
        requirements = (
            ["kubernetes"]
            + self._get_stack_requirements()
            + self._get_pipeline_requirements(pipeline)
        )
        logger.debug("Kubeflow docker container requirements: %s", requirements)

        build_docker_image(
            build_context_path=repository_root,
            image_name=image_name,
            requirements=requirements,
            base_image=self.custom_docker_base_image_name,
        )

        if Repository().get_active_stack().container_registry:
            push_docker_image(image_name)

    def run(
        self,
        zenml_pipeline: "BasePipeline",
        run_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Prepares the pipeline to be run on Kubeflow"""
        # Establish the connections between the components
        zenml_pipeline.connect(**zenml_pipeline.steps)

        # Create the final step list and the corresponding pipeline
        steps = [s.component for s in zenml_pipeline.steps.values()]

        artifact_store = zenml_pipeline.stack.artifact_store
        metadata_store = zenml_pipeline.stack.metadata_store

        created_pipeline = tfx_pipeline.Pipeline(
            pipeline_name=zenml_pipeline.name,
            components=steps,  # type: ignore[arg-type]
            pipeline_root=artifact_store.path,
            metadata_connection_config=metadata_store.get_tfx_metadata_config(),
            enable_cache=zenml_pipeline.enable_cache,
        )

        from zenml.integrations.kubeflow.docker_utils import get_image_digest

        image_name = self.get_docker_image_name(zenml_pipeline.pipeline_name)
        image_name = get_image_digest(image_name) or image_name

        fileio.make_dirs(self.pipeline_directory)
        pipeline_file_path = os.path.join(
            self.pipeline_directory, f"{zenml_pipeline.name}.yaml"
        )
        runner_config = KubeflowDagRunnerConfig(image=image_name)
        runner = KubeflowDagRunner(
            config=runner_config, output_path=pipeline_file_path
        )
        runner.run(created_pipeline)

        run_name = run_name or datetime.now().strftime("%d_%h_%y-%H_%M_%S_%f")
        self._upload_and_run_pipeline(
            pipeline_file_path=pipeline_file_path,
            run_name=run_name,
            enable_cache=zenml_pipeline.enable_cache,
        )

    def _upload_and_run_pipeline(
        self, pipeline_file_path: str, run_name: str, enable_cache: bool
    ) -> None:
        """Tries to upload and run a KFP pipeline.

        Args:
            pipeline_file_path: Path to the pipeline definition file.
            run_name: A name for the pipeline run that will be started.
            enable_cache: Whether caching is enabled for this pipeline run.
        """
        try:
            if self.kubernetes_context:
                logger.info(
                    "Running in kubernetes context '%s'.",
                    self.kubernetes_context,
                )

            # load kubernetes config to authorize the KFP client
            config.load_kube_config(context=self.kubernetes_context)

            # upload the pipeline to Kubeflow and start it
            client = kfp.Client()
            result = client.create_run_from_pipeline_package(
                pipeline_file_path,
                arguments={},
                run_name=run_name,
                enable_caching=enable_cache,
            )
            logger.info("Started pipeline run with ID '%s'.", result.run_id)
        except urllib3.exceptions.HTTPError as error:
            logger.warning(
                "Failed to upload Kubeflow pipeline: %s. "
                "Please make sure your kube config is configured and the "
                "current context is set correctly.",
                error,
            )

    def _get_stack_requirements(self) -> List[str]:
        """Gets list of requirements for the current active stack."""
        stack = Repository().get_active_stack()
        requirements = []

        artifact_store_module = stack.artifact_store.__module__
        requirements += get_requirements_for_module(artifact_store_module)

        metadata_store_module = stack.metadata_store.__module__
        requirements += get_requirements_for_module(metadata_store_module)

        return requirements

    def _get_pipeline_requirements(self, pipeline: "BasePipeline") -> List[str]:
        """Gets list of requirements for a pipeline."""
        if pipeline.requirements_file and fileio.file_exists(
            pipeline.requirements_file
        ):
            logger.debug(
                "Using requirements from file %s.", pipeline.requirements_file
            )
            with fileio.open(pipeline.requirements_file, "r") as f:
                return [
                    requirement.strip() for requirement in f.read().split("\n")
                ]
        else:
            return []

    @property
    def _pid_file_path(self) -> str:
        """Returns path to the daemon PID file."""
        return os.path.join(self.root_directory, "kubeflow_daemon.pid")

    @property
    def _k3d_cluster_name(self) -> str:
        """Returns the K3D cluster name."""
        # K3D only allows cluster names with up to 32 characters, use the
        # first 8 chars of the orchestrator UUID as identifier
        return f"zenml-kubeflow-{str(self.uuid)[:8]}"

    def _get_k3d_registry_name(self, port: int) -> str:
        """Returns the K3D registry name."""
        return f"k3d-zenml-kubeflow-registry.localhost:{port}"

    @property
    def _k3d_registry_config_path(self) -> str:
        """Returns the path to the K3D registry config yaml."""
        return os.path.join(self.root_directory, "k3d_registry.yaml")

    @property
    def is_running(self) -> bool:
        """Returns whether the orchestrator is running."""
        if not local_deployment_utils.check_prerequisites():
            # if any prerequisites are missing there is certainly no
            # local deployment running
            return False

        return local_deployment_utils.k3d_cluster_exists(
            cluster_name=self._k3d_cluster_name
        )

    def up(self) -> None:
        """Spins up a local Kubeflow Pipelines deployment."""
        if self.is_running:
            logger.info(
                "Found already existing local Kubeflow Pipelines deployment. "
                "If there are any issues with the existing deployment, please "
                "run 'zenml orchestrator down' to delete it."
            )
            return

        if not local_deployment_utils.check_prerequisites():
            logger.error(
                "Unable to spin up local Kubeflow Pipelines deployment: "
                "Please install 'k3d' and 'kubectl' and try again."
            )
            return

        container_registry = Repository().get_active_stack().container_registry
        if not container_registry:
            logger.error(
                "Unable to spin up local Kubeflow Pipelines deployment: "
                "Missing container registry in current stack."
            )
            return

        logger.info("Spinning up local Kubeflow Pipelines deployment...")
        fileio.make_dirs(self.root_directory)
        container_registry_port = int(container_registry.uri.split(":")[-1])
        container_registry_name = self._get_k3d_registry_name(
            port=container_registry_port
        )
        local_deployment_utils.write_local_registry_yaml(
            yaml_path=self._k3d_registry_config_path,
            registry_name=container_registry_name,
            registry_uri=container_registry.uri,
        )
        local_deployment_utils.create_k3d_cluster(
            cluster_name=self._k3d_cluster_name,
            registry_name=container_registry_name,
            registry_config_path=self._k3d_registry_config_path,
        )
        kubernetes_context = f"k3d-{self._k3d_cluster_name}"
        local_deployment_utils.deploy_kubeflow_pipelines(
            kubernetes_context=kubernetes_context
        )
        local_deployment_utils.start_kfp_ui_daemon(
            pid_file_path=self._pid_file_path, port=8080
        )

        logger.info(
            "Finished local Kubeflow Pipelines deployment. The UI should now "
            "be accessible at http://localhost:8080/."
        )

    def down(self) -> None:
        """Tears down a local Kubeflow Pipelines deployment."""
        if self.is_running:
            local_deployment_utils.delete_k3d_cluster(
                cluster_name=self._k3d_cluster_name
            )

        if fileio.file_exists(self._pid_file_path):
            from zenml.utils import daemon

            # TODO [ENG-234]: Update with smarter solution for windows daemon
            if sys.platform == "win32":
                pass
            else:
                daemon.stop_daemon(self._pid_file_path, kill_children=True)
                fileio.remove(self._pid_file_path)

        logger.info("Local kubeflow pipelines deployment spun down.")
