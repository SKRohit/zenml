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

from typing import TYPE_CHECKING, Any, Dict, Type

from zenml.exceptions import IntegrationError
from zenml.logger import get_logger

if TYPE_CHECKING:
    from zenml.integrations.integration import Integration

logger = get_logger(__name__)


class IntegrationRegistry(object):
    """Registry to keep track of ZenML Integrations"""

    def __init__(self) -> None:
        """Initializing the integration registry"""
        self._integrations: Dict[str, Type["Integration"]] = {}

    @property
    def integrations(self) -> Dict[str, Type["Integration"]]:
        """Method to get integrations dictionary.

        Returns:
            A dict of integration key to type of `Integration`.
        """
        return self._integrations

    @integrations.setter
    def integrations(self, i: Any) -> None:
        """Setter method for the integrations property"""
        raise IntegrationError(
            "Please do not manually change the integrations within the "
            "registry. If you would like to register a new integration "
            "manually, please use "
            "`integration_registry.register_integration()`."
        )

    def register_integration(
        self, key: str, type_: Type["Integration"]
    ) -> None:
        """Method to register an integration with a given name"""
        self._integrations[key] = type_

    def activate_integrations(self) -> None:
        """Method to activate the integrations with are registered in the
        registry"""
        for name, integration in self._integrations.items():
            if integration.check_installation():
                integration.activate()
                logger.debug(f"Integration `{name}` is activated.")
            else:
                logger.debug(f"Integration `{name}` could not be activated.")


integration_registry = IntegrationRegistry()
