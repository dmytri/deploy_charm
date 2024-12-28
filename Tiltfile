load('ext://namespace', 'namespace_create')
load('ext://k8s_attach', 'k8s_attach')

if k8s_namespace() != "telnik":
    fail("Must run in 'telnik' namespace")

namespace_create('telnik')

docker_build('target', 'target/')
k8s_yaml('target/manifest.yaml')
k8s_resource('target', port_forwards=[2222, 9418, 23231, 23232, 23233])

docker_build('apply', '.')
k8s_yaml('manifest.yaml')
k8s_resource('apply', resource_deps=['target'], auto_init=False, trigger_mode=TRIGGER_MODE_MANUAL)


