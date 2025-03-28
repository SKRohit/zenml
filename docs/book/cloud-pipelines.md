---
description: >-
  Swap out local stack for a cloud-based stack to get pipelines running in
  production.
---

# Run Your Pipelines in the Cloud

When users want to run pipelines on remote architecture, all they need to do is swap out their `local` stack with a cloud-based stack, which you can configure.

A stack is made up of the following three core components:

* An Artifact Store
* A Metadata Store
* An Orchestrator

A ZenML stack can be registered in the following way:

```bash
zenml stack register STACK_NAME \
    -m METADATA_STORE_NAME \
    -a ARTIFACT_STORE_NAME \
    -o ORCHESTRATOR_NAME
zenml stack set STACK_NAME  # turns it active
```

{% hint style="info" %}
See [CLI reference](../reference/cli-command-reference.md) for more help.
{% endhint %}

After a stack has been set as active, just running a pipeline will run that pipeline on the cloud stack instead of the local stack:

```python
python run.py  # will now run on a different orchestrator / stack
```

Let's see what different combinations of stacks exists:

## Metadata Stores

ZenML puts a lot of emphasis on guaranteed tracking of inputs across pipeline steps. The strict, fully automated, and deeply built-in tracking enables some of our most powerful features - e.g. comparability across pipelines. To achieve this, we're using a concept we call the Metadata Store.

You have the following options to configure your Metadata Store:

* SQLite (Default)
* MySQL

But this will be extended in the future to include MLFlow, wandb etc.

### SQLite (Default)

By default, your pipelines will be tracked in a local SQLite database within your `.zen` folder. There is not much configuration to it - it just works out of the box.

### MySQL

Using MySQL as a Metadata Store is where ZenML can become really powerful, especially in highly dynamic environments (read: running experiments locally, in the Cloud, and across team members). Some of the ZenML integrations even require a dedicated MySQL-based Metadata Store to unfold their true potential.

The Metadata Store can be simply configured to use any MySQL server (=>5.6):

```
zenml metadata register METADATA_STORE_NAME mysql \
    --host=127.0.0.1 \ 
    --port=3306 \
    --username=USER \
    --passwd=PASSWD \
    --database=DATABASE
```

One particular configuration our team is very fond of internally leverages Google Cloud SQL and the docker-based cloudsql proxy to track experiments across team members and environments. Stay tuned for a tutorial on that!

## Artifact Stores

Closely related to the [Metadata Store](https://github.com/zenml-io/zenml/blob/1b32b50007ef781b39c2525c3ca31ee03026c2b5/docs/book/repository/metadata-store.md) is the Artifact Store. It will store all intermediary pipeline step results, a binary representation of your source data as well as the trained model.

You have the following options to configure the Artifact Store:

* Local (Default)
* Remote (Google Cloud Storage)
  * **Soon**: AWS S3-compatible stacks

### Local (Default)

By default, ZenML will use the `.zen` directory created when you run `zenml init` at the very beginning. All artifacts and inputs will be persisted there.

Using the default Artifact Store can be a limitation to the integrations you might want to use. Please check the documentation of the individual integrations to make sure they are compatible.

### Remote (GCS/S3)

Many experiments and many ZenML integrations require a remote Artifact Store to reliable retrieve and persist pipeline step artifacts. Especially dynamic scenarios with heterogeneous environments will be only possible when using a remote Artifact Store.

Configuring a remote Artifact Store for ZenML is a one-liner using the CLI:

```
zenml artifact register ARTIFACT_STORE_NAME gcp --path=gs://your-bucket/sub/dir
```

## Orchestrator

The orchestrator is especially important, as it defines **where** the actual pipeline job runs. Think of it as the `root` of any pipeline job, that controls how and where each individual step within a pipeline is executed. Therefore, the orchestrator can be used to great effect to scale jobs in production.

### Standard Orchestrators

Please refer to the docstrings within the source code for precise details.

#### Local orchestrator

This is the default orchestrator for ZenML pipelines. It runs pipelines sequentially as a Python process in it's local environment. You can use this orchestrator for quick experimentation and work on smaller datasets in your local environment.

#### Airflow

Coming Soon!

#### GCP Orchestrator

Coming Soon!

The GCPOrchestrator can be found at `OrchestratorGCPBackend`. It spins up a VM on your GCP projects, zips up your local code to the instance, and executes the ZenML pipeline with a Docker Image of your choice.

Best of all, the Orchestrator is capable of launching preemtible VMs, saving a big chunk of cost along the way.

#### Kubernetes

Coming Soon!

The KubernetesOrchestrator launches a Job on your Kubernetes cluster, zips up your local code to the Pod, and executes the ZenML pipeline with a Docker Image of your choice.

#### AWS Orchestrator

Coming Soon!

#### Azure Orchestrator

Coming Soon!

#### Kubeflow

Coming soon!

### Creating a custom orchestrator

The API to create custom orchestrators is still under active development. Please see this space for updates.

If you would like to see this functionality earlier, please let us know via our [Slack Channel](https://zenml.io/slack-invite/) or create an issue on GitHub.
