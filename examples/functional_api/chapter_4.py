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

import numpy as np
import tensorflow as tf
from sklearn.base import ClassifierMixin
from sklearn.linear_model import LogisticRegression

from zenml.core.repo import Repository
from zenml.pipelines import pipeline
from zenml.steps import step
from zenml.steps.base_step_config import BaseStepConfig
from zenml.steps.step_output import Output


class TrainerConfig(BaseStepConfig):
    """Trainer params"""

    epochs: int = 1
    gamma: float = 0.7
    lr: float = 0.001


@step
def importer_mnist() -> Output(
    X_train=np.ndarray, y_train=np.ndarray, X_test=np.ndarray, y_test=np.ndarray
):
    """Download the MNIST data store it as an artifact"""
    (X_train, y_train), (
        X_test,
        y_test,
    ) = tf.keras.datasets.mnist.load_data()
    return X_train, y_train, X_test, y_test


@step
def normalize_mnist(
    X_train: np.ndarray, X_test: np.ndarray
) -> Output(X_train_normed=np.ndarray, X_test_normed=np.ndarray):
    """Normalize the values for all the images so they are between 0 and 1"""
    X_train_normed = X_train / 255.0
    X_test_normed = X_test / 255.0
    return X_train_normed, X_test_normed


@step
def tf_trainer(
    config: TrainerConfig,
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> tf.keras.Model:
    """Train a neural net from scratch to recognise MNIST digits return our
    model or the learner"""
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(10, activation="relu"),
            tf.keras.layers.Dense(10),
        ]
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(0.001),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )

    model.fit(
        X_train,
        y_train,
        epochs=config.epochs,
    )

    # write model
    return model


@step
def tf_evaluator(
    X_test: np.ndarray,
    y_test: np.ndarray,
    model: tf.keras.Model,
) -> float:
    """Calculate the loss for the model for each epoch in a graph"""

    _, test_acc = model.evaluate(X_test, y_test, verbose=2)
    return test_acc


@step
def sklearn_trainer(
    config: TrainerConfig,
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> ClassifierMixin:
    """Train SVC from sklearn."""
    clf = LogisticRegression(penalty="l1", solver="saga", tol=0.1)
    clf.fit(X_train.reshape((X_train.shape[0], -1)), y_train)
    return clf


@step
def sklearn_evaluator(
    X_test: np.ndarray,
    y_test: np.ndarray,
    model: ClassifierMixin,
) -> float:
    """Calculate accuracy score with classifier."""

    test_acc = model.score(X_test.reshape((X_test.shape[0], -1)), y_test)
    return test_acc


@pipeline
def mnist_pipeline(
    importer,
    normalizer,
    trainer,
    evaluator,
):
    # Link all the steps artifacts together
    X_train, y_train, X_test, y_test = importer()
    X_trained_normed, X_test_normed = normalizer(X_train=X_train, X_test=X_test)
    model = trainer(X_train=X_trained_normed, y_train=y_train)
    evaluator(X_test=X_test_normed, y_test=y_test, model=model)


# Run the pipeline
# Initialise a pipeline run
tf_p = mnist_pipeline(
    importer=importer_mnist(),
    normalizer=normalize_mnist(),
    trainer=tf_trainer(config=TrainerConfig(epochs=1)),
    evaluator=tf_evaluator(),
)

# Run the pipeline
tf_p.run()


# Initialise a new pipeline run
scikit_p = mnist_pipeline(
    importer=importer_mnist(),
    normalizer=normalize_mnist(),
    trainer=sklearn_trainer(config=TrainerConfig()),
    evaluator=sklearn_evaluator(),
)

# Run the new pipeline
scikit_p.run()

# Post execution flow
repo = Repository()
p = repo.get_pipeline(pipeline_name="mnist_pipeline")
print(f"Pipeline `mnist_pipeline` has {len(p.runs)} run(s)")
for r in p.runs[0:2]:
    eval_step = r.get_step("evaluator")
    print(
        f"For {eval_step.name}, the accuracy is: "
        f"{eval_step.output.read():.2f}"
    )
