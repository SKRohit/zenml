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

from typing import TYPE_CHECKING, Any, List

from zenml.logger import get_logger

if TYPE_CHECKING:
    from zenml.metadata.base_metadata_store import BaseMetadataStore
    from zenml.post_execution.pipeline_run import PipelineRunView

logger = get_logger(__name__)


class PipelineView:
    """Post-execution pipeline class which can be used to query
    pipeline-related information from the metadata store.
    """

    def __init__(
        self, id_: int, name: str, metadata_store: "BaseMetadataStore"
    ):
        """Initializes a post-execution pipeline object.

        In most cases `PipelineView` objects should not be created manually
        but retrieved using the `get_pipelines()` method of a
        `zenml.core.repo.Repository` instead.

        Args:
            id_: The context id of this pipeline.
            name: The name of this pipeline.
            metadata_store: The metadata store which should be used to fetch
                additional information related to this pipeline.
        """
        self._id = id_
        self._name = name
        self._metadata_store = metadata_store

    @property
    def name(self) -> str:
        """Returns the name of the pipeline."""
        return self._name

    @property
    def runs(self) -> List["PipelineRunView"]:
        """Returns all stored runs of this pipeline.

        The runs are returned in chronological order, so the latest
        run will be the last element in this list.
        """
        # Do not cache runs as new runs might appear during this objects
        # lifecycle
        runs = self._metadata_store.get_pipeline_runs(self)
        return list(runs.values())

    def get_run_names(self) -> List[str]:
        """Returns a list of all run names."""
        # Do not cache runs as new runs might appear during this objects
        # lifecycle
        runs = self._metadata_store.get_pipeline_runs(self)
        return list(runs.keys())

    def get_run(self, name: str) -> "PipelineRunView":
        """Returns a run for the given name.

        Args:
            name: The name of the run to return.

        Raises:
            KeyError: If there is no run with the given name.
        """
        run = self._metadata_store.get_pipeline_run(self, name)
        if not run:
            raise KeyError(
                f"No run found for name `{name}`. This pipeline "
                f"only has runs with the following "
                f"names: `{self.get_run_names()}`"
            )
        return run

    def __repr__(self) -> str:
        """Returns a string representation of this pipeline."""
        return (
            f"{self.__class__.__qualname__}(id={self._id}, "
            f"name='{self._name}')"
        )

    def __eq__(self, other: Any) -> bool:
        """Returns whether the other object is referring to the
        same pipeline."""
        if isinstance(other, PipelineView):
            return (
                self._id == other._id
                and self._metadata_store.uuid == other._metadata_store.uuid
            )
        return NotImplemented
