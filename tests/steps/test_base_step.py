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
from contextlib import ExitStack as does_not_raise
from typing import Optional

import pytest

from zenml.exceptions import MissingStepParameterError, StepInterfaceError
from zenml.materializers.base_materializer import BaseMaterializer
from zenml.materializers.built_in_materializer import BuiltInMaterializer
from zenml.steps import step
from zenml.steps.base_step_config import BaseStepConfig
from zenml.steps.step_context import StepContext
from zenml.steps.step_output import Output


def test_step_decorator_creates_class_in_same_module_as_decorated_function():
    """Tests that the `BaseStep` subclass created by our step decorator
    creates the class in the same module as the decorated function."""

    @step
    def some_step():
        pass

    assert some_step.__module__ == __name__


def test_define_step_with_shared_input_and_output_name():
    """Tests that defining a step with a shared input and output name raises
    a StepInterfaceError."""
    with pytest.raises(StepInterfaceError):

        @step
        def some_step(shared_name: int) -> Output(shared_name=int):
            return shared_name


def test_define_step_with_multiple_configs():
    """Tests that defining a step with multiple configs raises
    a StepInterfaceError."""
    with pytest.raises(StepInterfaceError):

        @step
        def some_step(
            first_config: BaseStepConfig, second_config: BaseStepConfig
        ):
            pass


def test_define_step_with_multiple_contexts():
    """Tests that defining a step with multiple contexts raises
    a StepInterfaceError."""
    with pytest.raises(StepInterfaceError):

        @step
        def some_step(first_context: StepContext, second_context: StepContext):
            pass


def test_define_step_without_input_annotation():
    """Tests that defining a step with a missing input annotation raises
    a StepInterfaceError."""
    with pytest.raises(StepInterfaceError):

        @step
        def some_step(some_argument, some_other_argument: int):
            pass


def test_define_step_with_variable_args():
    """Tests that defining a step with variable arguments raises
    a StepInterfaceError."""
    with pytest.raises(StepInterfaceError):

        @step
        def some_step(*args: int):
            pass


def test_define_step_with_variable_kwargs():
    """Tests that defining a step with variable keyword arguments raises
    a StepInterfaceError."""
    with pytest.raises(StepInterfaceError):

        @step
        def some_step(**kwargs: int):
            pass


def test_define_step_with_keyword_only_arguments():
    """Tests that keyword-only arguments get included in the input signature
    or a step."""

    @step
    def some_step(some_argument: int, *, keyword_only_argument: int):
        pass

    assert "keyword_only_argument" in some_step.INPUT_SIGNATURE


def test_initialize_step_with_unexpected_config():
    """Tests that passing a config to a step that was defined without
    config raises an Exception."""

    @step
    def step_without_config() -> None:
        pass

    with pytest.raises(StepInterfaceError):
        step_without_config(config=BaseStepConfig())


def test_initialize_step_with_config():
    """Tests that a step can only be initialized with it's defined
    config class."""

    class StepConfig(BaseStepConfig):
        pass

    class DifferentConfig(BaseStepConfig):
        pass

    @step
    def step_with_config(config: StepConfig) -> None:
        pass

    # initialize with wrong config classes
    with pytest.raises(StepInterfaceError):
        step_with_config(config=BaseStepConfig())  # noqa

    with pytest.raises(StepInterfaceError):
        step_with_config(config=DifferentConfig())  # noqa

    # initialize with wrong key
    with pytest.raises(StepInterfaceError):
        step_with_config(wrong_config_key=StepConfig())  # noqa

    # initializing with correct key should work
    with does_not_raise():
        step_with_config(config=StepConfig())

    # initializing as non-kwarg should work as well
    with does_not_raise():
        step_with_config(StepConfig())

    # initializing with multiple args or kwargs should fail
    with pytest.raises(StepInterfaceError):
        step_with_config(StepConfig(), config=StepConfig())

    with pytest.raises(StepInterfaceError):
        step_with_config(StepConfig(), StepConfig())

    with pytest.raises(StepInterfaceError):
        step_with_config(config=StepConfig(), config2=StepConfig())


def test_pipeline_parameter_name_is_empty_when_initializing_a_step():
    """Tests that the `pipeline_parameter_name` attribute is `None` when
    a step is initialized."""

    @step
    def some_step():
        pass

    assert some_step().pipeline_parameter_name is None


def test_access_step_component_before_calling():
    """Tests that accessing a steps component before calling it raises
    a StepInterfaceError."""

    @step
    def some_step():
        pass

    with pytest.raises(StepInterfaceError):
        _ = some_step().component


def test_access_step_component_after_calling():
    """Tests that a step component exists after the step was called."""

    @step
    def some_step():
        pass

    step_instance = some_step()
    step_instance()

    with does_not_raise():
        _ = step_instance.component


def test_configure_step_with_wrong_materializer_class():
    """Tests that passing a random class as a materializer raises a
    StepInterfaceError."""

    @step
    def some_step() -> Output(some_output=int):
        pass

    with pytest.raises(StepInterfaceError):
        some_step().with_return_materializers(str)  # noqa


def test_configure_step_with_wrong_materializer_key():
    """Tests that passing a materializer for a non-existent argument raises a
    StepInterfaceError."""

    @step
    def some_step() -> Output(some_output=int):
        pass

    with pytest.raises(StepInterfaceError):
        materializers = {"some_nonexistent_output": BaseMaterializer}
        some_step().with_return_materializers(materializers)


def test_configure_step_with_wrong_materializer_class_in_dict():
    """Tests that passing a wrong class as materializer for a specific output
    raises a StepInterfaceError."""

    @step
    def some_step() -> Output(some_output=int):
        pass

    materializers = {"some_output": "not_a_materializer_class"}
    with pytest.raises(StepInterfaceError):
        some_step().with_return_materializers(materializers)  # noqa


def test_setting_a_materializer_for_a_step_with_multiple_outputs():
    """Tests that setting a materializer for a step with multiple outputs
    sets the materializer for all the outputs."""

    @step
    def some_step() -> Output(some_output=int, some_other_output=str):
        pass

    step_instance = some_step().with_return_materializers(BaseMaterializer)
    assert step_instance.get_materializers()["some_output"] is BaseMaterializer
    assert (
        step_instance.get_materializers()["some_other_output"]
        is BaseMaterializer
    )


def test_overwriting_step_materializers():
    """Tests that calling `with_return_materializers` multiple times allows
    overwriting of the step materializers."""

    @step
    def some_step() -> Output(some_output=int, some_other_output=str):
        pass

    step_instance = some_step()
    assert not step_instance._explicit_materializers

    step_instance = step_instance.with_return_materializers(
        {"some_output": BaseMaterializer}
    )
    assert (
        step_instance._explicit_materializers["some_output"] is BaseMaterializer
    )
    assert "some_other_output" not in step_instance._explicit_materializers

    step_instance = step_instance.with_return_materializers(
        {"some_other_output": BuiltInMaterializer}
    )
    assert (
        step_instance._explicit_materializers["some_other_output"]
        is BuiltInMaterializer
    )
    assert (
        step_instance._explicit_materializers["some_output"] is BaseMaterializer
    )

    step_instance = step_instance.with_return_materializers(
        {"some_output": BuiltInMaterializer}
    )
    assert (
        step_instance._explicit_materializers["some_output"]
        is BuiltInMaterializer
    )

    step_instance.with_return_materializers(BaseMaterializer)
    assert (
        step_instance._explicit_materializers["some_output"] is BaseMaterializer
    )
    assert (
        step_instance._explicit_materializers["some_other_output"]
        is BaseMaterializer
    )


def test_step_with_disabled_cache_has_random_string_as_execution_property():
    """Tests that a step with disabled caching adds a random string as
    execution property to disable caching."""

    @step(enable_cache=False)
    def some_step():
        pass

    step_instance_1 = some_step()
    step_instance_2 = some_step()

    assert (
        step_instance_1._internal_execution_parameters["zenml-disable_cache"]
        != step_instance_2._internal_execution_parameters["zenml-disable_cache"]
    )


def test_step_source_execution_parameter_stays_the_same_if_step_is_not_modified():
    """Tests that the step source execution parameter remains constant when
    creating multiple steps from the same source code."""

    @step
    def some_step():
        pass

    step_1 = some_step()
    step_2 = some_step()

    assert (
        step_1._internal_execution_parameters["zenml-step_source"]
        == step_2._internal_execution_parameters["zenml-step_source"]
    )


def test_step_source_execution_parameter_changes_when_signature_changes():
    """Tests that modifying the input arguments or outputs of a step
    function changes the step source execution parameter."""

    @step
    def some_step(some_argument: int) -> int:
        pass

    step_1 = some_step()

    @step
    def some_step(some_argument_with_new_name: int) -> int:
        pass

    step_2 = some_step()

    assert (
        step_1._internal_execution_parameters["zenml-step_source"]
        != step_2._internal_execution_parameters["zenml-step_source"]
    )

    @step
    def some_step(some_argument: int) -> str:
        pass

    step_3 = some_step()

    assert (
        step_1._internal_execution_parameters["zenml-step_source"]
        != step_3._internal_execution_parameters["zenml-step_source"]
    )


def test_step_source_execution_parameter_changes_when_function_body_changes():
    """Tests that modifying the step function code changes the step
    source execution parameter."""

    @step
    def some_step():
        pass

    step_1 = some_step()

    @step
    def some_step():
        # this is new
        pass

    step_2 = some_step()

    assert (
        step_1._internal_execution_parameters["zenml-step_source"]
        != step_2._internal_execution_parameters["zenml-step_source"]
    )


def test_materializer_source_execution_parameter_changes_when_materializer_changes():
    """Tests that changing the step materializer changes the materializer
    source execution parameter."""

    @step
    def some_step() -> int:
        return 1

    class MyCustomMaterializer(BuiltInMaterializer):
        pass

    step_1 = some_step().with_return_materializers(BuiltInMaterializer)
    step_2 = some_step().with_return_materializers(MyCustomMaterializer)

    key = "zenml-output_materializer_source"
    assert (
        step_1._internal_execution_parameters[key]
        != step_2._internal_execution_parameters[key]
    )


def test_call_step_with_args(int_step_output, step_with_two_int_inputs):
    """Test that a step can be called with args."""
    with does_not_raise():
        step_with_two_int_inputs()(int_step_output, int_step_output)


def test_call_step_with_kwargs(int_step_output, step_with_two_int_inputs):
    """Test that a step can be called with kwargs."""
    with does_not_raise():
        step_with_two_int_inputs()(
            input_1=int_step_output, input_2=int_step_output
        )


def test_call_step_with_args_and_kwargs(
    int_step_output, step_with_two_int_inputs
):
    """Test that a step can be called with a mix of args and kwargs."""
    with does_not_raise():
        step_with_two_int_inputs()(int_step_output, input_2=int_step_output)


def test_call_step_with_too_many_args(
    int_step_output, step_with_two_int_inputs
):
    """Test that calling a step fails when too many args
    are passed."""
    with pytest.raises(StepInterfaceError):
        step_with_two_int_inputs()(
            int_step_output, int_step_output, int_step_output
        )


def test_call_step_with_too_many_args_and_kwargs(
    int_step_output, step_with_two_int_inputs
):
    """Test that calling a step fails when too many args
    and kwargs are passed."""
    with pytest.raises(StepInterfaceError):
        step_with_two_int_inputs()(
            int_step_output, input_1=int_step_output, input_2=int_step_output
        )


def test_call_step_with_missing_key(int_step_output, step_with_two_int_inputs):
    """Test that calling a step fails when an argument
    is missing."""
    with pytest.raises(StepInterfaceError):
        step_with_two_int_inputs()(input_1=int_step_output)


def test_call_step_with_unexpected_key(
    int_step_output, step_with_two_int_inputs
):
    """Test that calling a step fails when an argument
    has an unexpected key."""
    with pytest.raises(StepInterfaceError):
        step_with_two_int_inputs()(
            input_1=int_step_output,
            input_2=int_step_output,
            input_3=int_step_output,
        )


def test_call_step_with_wrong_arg_type(
    int_step_output, step_with_two_int_inputs
):
    """Test that calling a step fails when an arg has a wrong type."""
    with pytest.raises(StepInterfaceError):
        step_with_two_int_inputs()(1, int_step_output)


def test_call_step_with_wrong_kwarg_type(
    int_step_output, step_with_two_int_inputs
):
    """Test that calling a step fails when an kwarg has a wrong type."""
    with pytest.raises(StepInterfaceError):
        step_with_two_int_inputs()(input_1=1, input_2=int_step_output)


def test_call_step_with_missing_materializer_for_type():
    """Tests that calling a step with an output without registered
    materializer raises a StepInterfaceError."""

    class MyTypeWithoutMaterializer:
        pass

    @step
    def some_step() -> MyTypeWithoutMaterializer:
        return MyTypeWithoutMaterializer()

    with pytest.raises(StepInterfaceError):
        some_step()()


def test_call_step_with_default_materializer_registered():
    """Tests that calling a step with a registered default materializer for the
    output works."""

    class MyType:
        pass

    class MyTypeMaterializer(BaseMaterializer):
        ASSOCIATED_TYPES = [MyType]

    @step
    def some_step() -> MyType:
        return MyType()

    with does_not_raise():
        some_step()()


def test_step_uses_config_class_default_values_if_no_config_is_passed():
    """Tests that a step falls back to the config class default values if
    no config object is passed at initialization."""

    class ConfigWithDefaultValues(BaseStepConfig):
        some_parameter: int = 1

    @step
    def some_step(config: ConfigWithDefaultValues):
        pass

    # don't pass the config when initializing the step
    step_instance = some_step()
    step_instance._update_and_verify_parameter_spec()

    assert step_instance.PARAM_SPEC["some_parameter"] == 1


def test_step_fails_if_config_parameter_value_is_missing():
    """Tests that a step fails if no config object is passed at
    initialization and the config class misses some default values."""

    class ConfigWithoutDefaultValues(BaseStepConfig):
        some_parameter: int

    @step
    def some_step(config: ConfigWithoutDefaultValues):
        pass

    # don't pass the config when initializing the step
    step_instance = some_step()

    with pytest.raises(MissingStepParameterError):
        step_instance._update_and_verify_parameter_spec()


def test_step_config_allows_none_as_default_value():
    """Tests that `None` is allowed as a default value for a
    step config field."""

    class ConfigWithNoneDefaultValue(BaseStepConfig):
        some_parameter: Optional[int] = None

    @step
    def some_step(config: ConfigWithNoneDefaultValue):
        pass

    # don't pass the config when initializing the step
    step_instance = some_step()

    with does_not_raise():
        step_instance._update_and_verify_parameter_spec()
