# Deploy Charm

This repository contains the deployment configurations and tests for the Charmebracelet Soft Serve

## Setting Up the Environment

To set up a local Kubernetes environment, we recommend using Minikube along with Tilt for managing the development environment.

### Prerequisites

- Install [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- Install [Kubectl](https://kubernetes.io/docs/tasks/tools/)
- Install [Tilt](https://docs.tilt.dev/install.html)

### Starting Minikube

1. Start Minikube with the desired Kubernetes version:
    ```bash
    minikube start
    ```

### Using Tilt

1. Navigate to the root directory of your repository.
2. Start Tilt:
    ```bash
    tilt up --namespace=charm
    ```

Tilt will automatically apply the necessary Kubernetes manifests and manage your development environment.

### Accessing Your Application

Tilt will handle port forwarding and other necessary configurations. You can access your application using the forwarded ports defined in the `Tiltfile`.

- Manually trigger the "apply" resource, this will deploy Soft Serve to the target resource
- you can access Soft Serve via ssh
```bash
ssh localhost -p 23231

```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
