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

from abc import abstractmethod

from zenml.artifacts import DataArtifact, SchemaArtifact, StatisticsArtifact
from zenml.steps.base_step import BaseStep
from zenml.steps.base_step_config import BaseStepConfig
from zenml.steps.step_context import StepContext
from zenml.steps.step_output import Output


class BasePreprocesserConfig(BaseStepConfig):
    """Base class for Preprocesser step configurations"""


class BasePreprocesserStep(BaseStep):
    """Base step implementation for any Preprocesser step implementation on
    ZenML"""

    STEP_INNER_FUNC_NAME = "entrypoint"

    @abstractmethod
    def entrypoint(  # type: ignore[override]
        self,
        train_dataset: DataArtifact,
        test_dataset: DataArtifact,
        validation_dataset: DataArtifact,
        statistics: StatisticsArtifact,
        schema: SchemaArtifact,
        config: BasePreprocesserConfig,
        context: StepContext,
    ) -> Output(  # type:ignore[valid-type]
        train_transformed=DataArtifact,
        test_transformed=DataArtifact,
        valdation_transformed=DataArtifact,
    ):
        """Base entrypoint for any Preprocesser implementation"""
