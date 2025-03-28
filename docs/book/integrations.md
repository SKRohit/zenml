---
description: Use these tools out-of-the-box with ZenML.
---

# Integrations

**ZenML** integrates with many different third-party tools.

Once code is organized into a ZenML pipeline, you can supercharge your ML development with powerful integrations on multiple [MLOps stacks](core-concepts.md). There are lots of moving parts for all the MLOps tooling and infrastructure you require for ML in production and ZenML aims to bring it all together under one roof.

We currently support [Airflow](https://airflow.apache.org/) and [Kubeflow](https://www.kubeflow.org/) as third-party orchestrators for your ML pipeline code. ZenML steps can be built from any of the other tools you usually use in your ML workflows, from [`scikit-learn`](https://scikit-learn.org/stable/) to [`PyTorch`](https://pytorch.org/) or [`TensorFlow`](https://www.tensorflow.org/).

![ZenML is the glue](assets/zenml-is-the-glue.jpeg)

These are the third-party integrations that ZenML currently supports:

| Integration        | Status | Type                   | Implementation Notes                                                                | Example                                                                               |
| ------------------ | ------ | ---------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Apache Airflow     | ✅      | Orchestrator           | Works for local environment                                                         | [airflow_local](https://github.com/zenml-io/zenml/tree/main/examples/airflow_local)   |
| Apache Beam        | ✅      | Distributed Processing |                                                                                     |                                                                                       |
| BentoML            | ⛏      | Cloud                  | Looking for community implementors                                                  |                                                                                       |
| Dash               | ✅      | Visualizer             | For Pipeline and PipelineRun visualization objects.                                 | [lineage](https://github.com/zenml-io/zenml/tree/main/examples/lineage)               |
| Evidently          | ⛏      | Monitoring             | Looking for community implementors                                                  |                                                                                       |
| Facets             | ✅      | Visualizer             |                                                                                     | [statistics](https://github.com/zenml-io/zenml/tree/main/examples/statistics)         |
| GCP                | ✅      | Cloud                  |                                                                                     |                                                                                       |
| Graphviz           | ✅      | Visualizer             | For Pipeline and PipelineRun visualization objects.                                 | [dag_visualizer](https://github.com/zenml-io/zenml/tree/main/examples/dag_visualizer) |
| Great Expectations | ⛏      | Data Validation        | Looking for community implementors                                                  |                                                                                       |
| KServe             | ⛏      | Inference              | Looking for community implementors                                                  |                                                                                       |
| Kubeflow           | ✅      | Orchestrator           | Either full Kubeflow or Kubeflow Pipelines. Works for local environments currently. | [kubeflow](https://github.com/zenml-io/zenml/tree/main/examples/kubeflow)             |
| MLFlow             | ⛏      | Orchestrator           | Looking for community implementors                                                  |                                                                                       |
| numpy              | ✅      | Exploration            |                                                                                     |                                                                                       |
| pandas             | ✅      | Exploration            |                                                                                     |                                                                                       |
| Plotly             | ✅      | Visualizer             | For Pipeline and PipelineRun visualization objects.                                 | [lineage](https://github.com/zenml-io/zenml/tree/main/examples/lineage)               |
| PyTorch            | ✅      | Training               |                                                                                     |                                                                                       |
| PyTorch Lightning  | ✅      | Training               |                                                                                     |                                                                                       |
| scikit-learn       | ✅      | Training               |                                                                                     | [caching chapter](https://docs.zenml.io/guides/functional-api/chapter-4)               |
| Seldon             | ⛏      | Cloud                  | Looking for community implementors                                                  |                                                                                       |
| Tensorflow         | ✅      | Training               |                                                                                     | [quickstart](https://github.com/zenml-io/zenml/tree/main/examples/quickstart)         |
| Whylogs            | ⛏      | Logging                | Looking for community implementors                                                  |                                                                                       |

✅ means the integration is already implemented.
⛏ means we are looking to implement the integration soon.

## Help us with integrations!

There are many tools in the ML / MLOps field. We have made an initial prioritization of which tools to support with integrations, but we also welcome community contributions. Check our [Contributing Guide](CONTRIBUTING.md) for more details on how best to contribute.