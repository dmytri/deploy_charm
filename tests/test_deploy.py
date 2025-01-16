from io import StringIO
from textwrap import dedent
from typing import Literal, TypedDict

from pyinfra.api.config import Config
from pyinfra.api.connect import connect_all
from pyinfra.api.host import Host
from pyinfra.api.inventory import Inventory
from pyinfra.api.operation import add_op
from pyinfra.api.operations import run_ops
from pyinfra.api.state import State
from pyinfra.facts.apk import ApkPackages
from pyinfra.facts.openrc import OpenrcEnabled, OpenrcStatus
from pyinfra.facts.server import Arch, LinuxDistribution, LinuxDistributionDict
from pyinfra.operations import apk, files, openrc, server
from pytest import fixture, skip
from pytest_bdd import given, scenario, scenarios, then, when

## GLOBALS AND FIXTURES ~
#

Targets = Literal["ci", "dev", "prod"] 
TARGET: Targets | None = None

@fixture
def host(state: State) -> Host:
    assert state.inventory.hosts
    host: Host = list(state.inventory.hosts.values())[0]

    assert host is not None
    return host

@fixture
def state() -> State:
    global TARGET
    assert TARGET is not None
    match TARGET:
        case "dev":
            inventory: Inventory = Inventory((
                ["localhost"],
                {
                    "ssh_user": "root",
                    "ssh_port": 2222,
                    "ssh_password": "xxxxxxxx",
                    "ssh_strict_host_key_checking": "off",
                    "ssh_known_hosts_file": "/dev/null",
                }
            ))
        case "ci":
            inventory: Inventory = Inventory((
                ["ssh-service"],
                {
                    "ssh_user": "root",
                    "ssh_port": 2222,
                    "ssh_password": "xxxxxxxx",
                    "ssh_strict_host_key_checking": "off",
                    "ssh_known_hosts_file": "/dev/null",
                }
            ))
        case "prod":
            inventory: Inventory = Inventory((
                ["teknik.net"],
                {
                    "ssh_user": "dk",
                    "ssh_port": 22,
                    "ssh_password": "xxxxxxxx",
                    "ssh_strict_host_key_checking": "off",
                    "ssh_known_hosts_file": "/dev/null",
                }
            ))

        case _:
            raise Exception("invalid target environment")

    state = State(inventory, Config())

    state.print_input = True
    state.print_output = True
    state.print_fact_info = True
    state.print_noop_info = True

    connect_all(state)

    return state

SOFT_SERVE_VERSION: str | None = None

class SoftServe(TypedDict):
    version: str
    pkg: str

@fixture
def soft_serve(host: Host) -> SoftServe:
    global SOFT_SERVE_VERSION
    assert SOFT_SERVE_VERSION is not None
    version: str = SOFT_SERVE_VERSION
    arch: str = host.get_fact(Arch)
    assert arch in ["aarch64", "armv7", "x86", "x86_64"] 
    pkg: str = f"soft-serve_{version}_{arch}.apk"
    return {'version': version, "pkg": pkg}

DEPLOYED: bool = False

@fixture
def deployed() -> bool:
    assert (isinstance(DEPLOYED, bool))
    return DEPLOYED

## SCENARIOS ~
#

scenarios("deploy.feature")


## PREFLIGHT SCENARIOS
#

scenario("deploy.feature", "dev")

@when("target is dev")
def _():
    global TARGET
    assert TARGET is None
    TARGET = "dev"

scenario("deploy.feature", "ci")

@when("target is ci")
def _():
    global TARGET
    assert TARGET is None

    TARGET = "ci"

scenario("deploy.feature", "prod")

@when("target is prod")
def _():
    global TARGET
    assert TARGET is None
    TARGET = "prod"

scenario("deploy.feature", "Soft Serve Deployment is needed")

@given("Soft Serve v0.8.2")
def _():
    global SOFT_SERVE_VERSION
    SOFT_SERVE_VERSION = "0.8.2"

@then("deploy Soft Serve")
def _(host: Host, soft_serve: SoftServe):
    global DEPLOYED
    version: str = soft_serve["version"]
    packages: dict = host.get_fact(ApkPackages)
    if "soft-serve" in packages and packages["soft-serve"] == {version}:
        DEPLOYED = True
        skip()

## DEPLOY SCENARIOS ~
#

scenario("deploy.feature", "Expected host OS")

@given("the system packages are up to date")
def _(state: State, deployed: bool):
    if deployed:
        skip()

    add_op(state,
       apk.update
    )
    add_op(state,
       apk.upgrade
    )

@when("cosign is available for verification")
def _(state: State):
    add_op(state,
       apk.packages,
       packages = ["cosign"]
    )

    run_ops(state)

@then("OS is Alpine Linux 3.21")
def _(host: Host):
    distro: LinuxDistributionDict = host.get_fact(LinuxDistribution)
    assert distro["release_meta"]["PRETTY_NAME"] == "Alpine Linux v3.21"

scenario("deploy.feature", "Require Soft Serve")

@when("the Soft Serve package is downloaded")
def _(state: State, soft_serve: SoftServe):
    version: str = soft_serve["version"]
    pkg: str = soft_serve["pkg"]

    add_op(state,
        files.download,
        name="Download Soft Serve Binary",
        src=f"https://github.com/charmbracelet/soft-serve/releases/download/v{version}/{pkg}",
        dest=f"/root/{pkg}"
    )

@when("Soft Serve checksums file is required")
def _(state: State, soft_serve: SoftServe):
    version: str = soft_serve["version"]
    add_op(state,
        files.download,
        name="Download Soft Serve Checksums",
        src=f"https://github.com/charmbracelet/soft-serve/releases/download/v{version}/checksums.txt",
        dest="/root/checksums.txt"
    )

@when("the checksums file signature is verified")
def _(state: State, soft_serve: SoftServe, deployed: bool):

    if deployed:
        skip()

    version: str = soft_serve["version"]
    verify: str = dedent(
        f"""
        cosign verify-blob \
          --certificate-identity 'https://github.com/charmbracelet/meta/.github/workflows/goreleaser.yml@refs/heads/main' \
          --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
          --cert 'https://github.com/charmbracelet/soft-serve/releases/download/v{version}/checksums.txt.pem' \
          --signature 'https://github.com/charmbracelet/soft-serve/releases/download/v{version}/checksums.txt.sig' \
          ./checksums.txt
        """).strip()

    add_op(
        state,
        server.shell,
        name="verify checksums",
        commands=verify
    )

@when("the package integrity is verified")
def _(state, soft_serve):
    pkg: str = soft_serve["pkg"]
    match = dedent(
        f"""
       grep {pkg} checksums.txt > {pkg}.checksum
       sha256sum -c {pkg}.checksum
        """).strip()

    add_op(
        state,
        server.shell,
        name="verify checksum",
        commands=match
    )

@when("Soft Serve is installed and configured")
def _(state: State, host: Host, soft_serve: SoftServe):

    pkg: str = soft_serve["pkg"]

    add_op(
        state,
        server.shell,
        name="Install local APK",
        commands=f"apk add --allow-untrusted /root/{pkg}"
    )

    status: dict = host.get_fact(OpenrcStatus, "default")

    if "soft-serve" not in status:
        service: StringIO = StringIO(dedent(
            """
            #!/sbin/openrc-run

            name="Soft Serve"
            description="Soft Serve Git Server 🍦"
            command="/usr/bin/soft"
            command_args="serve"
            pidfile="/run/{RC_SVCNAME}.pid"
            start_stop_daemon_args="--background"

            depend() {
                need net
            }
            """).strip()
        )

        add_op(
            state,
            files.put,
            src=service,
            dest="/etc/init.d/soft-serve"
        )

        add_op(
            state,
            files.file,
            path="/etc/init.d/soft-serve",
            mode=755
        )

        add_op(
            state,
            openrc.service,
            "soft-serve",
            enabled=True
        )

    run_ops(state)

@then("Soft Serve is running and accessible")
def _(host: Host):
    enabled: dict = host.get_fact(OpenrcEnabled, "default")
    assert enabled['soft-serve'] is True
