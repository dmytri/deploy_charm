# Deploy Charmbracelet Soft Serve

Deploy Soft Serve with Behaviour Driven Automation (BDA)

## Behavior-Driven Automation (BDA)

Behavior-Driven Automation (BDA) is an approach that extends the principles of
Behavior-Driven Development (BDD) to automate processes and workflows, in this
example, configuration as code to deploy a Git server.

In this project, the `tests/deploy.feature` file and the `tests/test_deploy.py`
file work together to describe and automate the deployment process for the
Charmebracelet Soft Serve Git Host.
Automation:

1. **Feature File (`tests/deploy.feature`)**:
   - The feature file is written in Gherkin syntax, which describes the
   behavior of the system in a natural language format.
   - It contains multiple scenarios that outline different aspects of the
   deployment process, such as deploying to different environments (dev, ci,
   prod), ensuring the correct version of Soft Serve is deployed, and verifying
   the host OS.

2. **Test File (`tests/test_deploy.py`)**:
   - The test file uses the `pytest-bdd` library to link the scenarios
   described in the feature file to the actual automation code.
   - It defines fixtures and functions that implement the steps described in
   the feature file, such as setting the target environment, downloading and
   verifying packages, and ensuring the correct services are running.

Here's a breakdown of how the test file implements Behavior-Driven Automation:

- **Fixtures**: The test file defines several fixtures to set up the necessary
state and context for the tests. For example, the `state` fixture sets up the
inventory and configuration for the target environment.

- **Scenarios and Steps**: The test file uses the `scenario` decorator to link
each scenario in the feature file to the corresponding functions that implement
the steps. For example, the `@when("target is dev")` function sets the target
environment to "dev", and the `@when("Soft Serve is required")` function
handles the deployment of the Soft Serve package.

- **Facts and Operations**: The test file uses the `pyinfra` library to gather
facts and perform various operations, such as downloading files, verifying
checksums, and managing services. These operations

## Setting Up the Environment

To set up a local Kubernetes environment, we recommend using Minikube along
with Tilt for managing the development environment.

### Prerequisites

- Install [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- Install [Kubectl](https://kubernetes.io/docs/tasks/tools/)
- Install [Tilt](https://docs.tilt.dev/install.html)

Note, KinD or Docker Desktop Kubernetes may also work, but have not been tested.

### Starting Minikube

1. Start Minikube ```bash minikube start ```

### Using Tilt

1. Navigate to the root directory of your repository.
2. Start Tilt: ```bash tilt up --namespace=charm ```

Tilt will automatically apply the necessary Kubernetes manifests to deploy a
target alpine linux container with OpenSSH and OpenRC as a test host, and
provide a resource that can be manually triggered to create a container with
the BDA code and apply it to the target.

### Accessing Your Application

Tilt will handle port forwarding and other necessary configurations. You can
access your application using the forwarded ports defined in the `Tiltfile`.

- Manually trigger the "apply" resource, this will deploy Soft Serve to the
target resource
- you can access Soft Serve via ssh ```bash ssh localhost -p 23231

```
