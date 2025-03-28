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
from typing import Any

from zenml.logger import get_logger
from zenml.post_execution.pipeline_run import PipelineRunView
from zenml.visualizers.base_visualizer import BaseVisualizer

logger = get_logger(__name__)


class BasePipelineRunVisualizer(BaseVisualizer):
    """The base implementation of a ZenML Pipeline Run Visualizer."""

    @abstractmethod
    def visualize(
        self, object: PipelineRunView, *args: Any, **kwargs: Any
    ) -> None:
        """Method to visualize pipeline runs."""
