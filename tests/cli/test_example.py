#  Copyright (c) ZenML GmbH 2020. All Rights Reserved.

#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:

#       http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

# TODO [LOW]: Add tests for example pulling back in with more solid logic.

# import os
# from contextlib import ExitStack as does_not_raise
# from datetime import datetime
# from pathlib import Path
# from typing import List
#
# import pytest
#
# from zenml.cli.example import Example, ExamplesRepo, GitExamplesHandler
# from zenml.io import fileio
# from zenml.logger import get_logger
#
# logger = get_logger(__name__)
#
# ZERO_FIVE_ZERO_RELEASE_EXAMPLES = ["airflow", "legacy", "quickstart"]
# NOT_ZERO_FIVE_RELEASE_EXAMPLES = ["not_airflow", "not_legacy", "not_quickstart"]
# BAD_VERSIONS = ["aaa", "999999", "111111"]
#
#
# class MockCommit:
#     def __init__(self, committed_datetime: datetime):
#         self.committed_datetime = committed_datetime
#
#
# class MockTag:
#     def __init__(self, name: str, commit: MockCommit) -> None:
#         self.name = name
#         self.commit = commit
#
#
# class MockRepo:
#     def __init__(self, tags: List[MockTag]) -> None:
#         self.tags = tags
#
#
# @pytest.fixture(scope="session")
# def monkeypatch_session():
#     from _pytest.monkeypatch import MonkeyPatch
#
#     m = MonkeyPatch()
#     yield m
#     m.undo()
#
#
# @pytest.fixture(scope="session")
# def examples_repo(tmpdir_factory, monkeypatch_session):
#     tmp_path = tmpdir_factory.mktemp("zenml_examples")
#     fileio.copy_dir(os.getcwd(), str(tmp_path))
#     examples_repo = ExamplesRepo(cloning_path=tmp_path)
#
#     def empty():
#         return None
#
#     monkeypatch_session.setattr(examples_repo, "clone", empty)
#     monkeypatch_session.setattr(examples_repo, "delete", empty)
#     # Once you copy with fileio some scripts change their modes and get
#     # `modified`. We need to stash these changes to get the tests working.
#     examples_repo.repo.git.stash()
#     yield examples_repo
#
#
# @pytest.fixture(scope="session")
# def git_examples_handler(monkeypatch_session, examples_repo):
#     handler = GitExamplesHandler()
#     monkeypatch_session.setattr(handler, "examples_repo", examples_repo)
#     yield handler
#     handler.examples_repo.repo.git.stash()
#     handler.examples_repo.checkout("main")
#
#
# def test_check_if_latest_release_works(examples_repo, monkeypatch):
#     """Tests to see that latest_release gets the latest_release"""
#     mock_tags = [
#         MockTag("0.5.0", MockCommit(datetime(2021, 5, 17))),
#         MockTag("0.5.1", MockCommit(datetime(2021, 7, 17))),
#         MockTag("0.5.2", MockCommit(datetime(2021, 9, 17))),
#     ]
#     mock_repo = MockRepo(tags=mock_tags)
#     monkeypatch.setattr(examples_repo, "repo", mock_repo)
#
#     assert examples_repo.latest_release == "0.5.2"
#
#
# @pytest.mark.parametrize("example", ZERO_FIVE_ZERO_RELEASE_EXAMPLES)
# def test_list_returns_three_examples_for_0_5_0_release(
#     example: str, git_examples_handler: GitExamplesHandler
# ) -> None:
#     """Check the examples returned from zenml example list"""
#     git_examples_handler.pull(version="0.5.0")
#     assert example in [
#         example_instance.name
#         for example_instance in git_examples_handler.examples
#     ]
#
#
# def test_pull_earlier_version_does_not_fail(
#     git_examples_handler: GitExamplesHandler,
# ) -> None:
#     """Check pull of earlier version exits without errors"""
#     with does_not_raise():
#         git_examples_handler.pull(version="0.3.8")
#
#
# def test_pull_of_higher_version_than_currently_in_global_config_store(
#     git_examples_handler: GitExamplesHandler,
# ) -> None:
#     """Check what happens when (valid) desired version for a force redownload
#     is higher than the latest version stored in the global config"""
#     with does_not_raise():
#         git_examples_handler.pull(version="5.1")
#
#
# def test_info_echos_out_readme_content(
#     git_examples_handler: GitExamplesHandler,
# ) -> None:
#     """Check that info subcommand displays readme content"""
#     examples = git_examples_handler.examples
#     for example_instance in examples:
#         with does_not_raise():
#             assert example_instance.name is not None
#             assert example_instance.readme_content is not None
#
#
# def test_readme_content_fails_when_bad_directory_input() -> None:
#     """Check that readme_content fails when no readme is present"""
#     mock_example = Example(name="mock", path=Path("test"))
#     with pytest.raises(FileNotFoundError):
#         mock_example.readme_content
#
#
# def test_readme_content_fails_when_no_readme_present(tmp_path) -> None:
#     """Check that readme_content fails when no readme is present"""
#     mock_example = Example(name="mock", path=Path(tmp_path))
#     with pytest.raises(ValueError):
#         mock_example.readme_content
