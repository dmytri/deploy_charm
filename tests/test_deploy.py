from pytest import fixture
from pytest_bdd import scenarios, scenario, given, when, then
from pyinfra.api.host import Host
from pyinfra.api.inventory import Inventory
from pyinfra.api.operation import add_op
from pyinfra.api.operations import run_ops
from pyinfra.api.connect import connect_all
from pyinfra.api.state import State
from pyinfra.api.config import Config
from pyinfra.facts.server import LinuxDistribution, LinuxDistributionDict, Arch
from pyinfra.facts.apk import ApkPackages
from pyinfra.facts.openrc import OpenrcStatus, OpenrcEnabled
from pyinfra.operations import files, server, apk, openrc

from typing import Literal
from io import StringIO
from textwrap import dedent

scenarios("deploy.feature")

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
                },
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
                },
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

scenario("deploy.feature", "Verify expected host OS")

@given("apk packages must be latest")
def _(state):
    add_op(state,
       apk.update
    )
    add_op(state,
       apk.upgrade
    )
    run_ops(state)

@then("OS is Alpine Linux 3.21")
def _(host: Host):
    distro: LinuxDistributionDict = host.get_fact(LinuxDistribution)
    assert distro["release_meta"]["PRETTY_NAME"] == "Alpine Linux v3.21"

scenario("deploy.feature", "Verify Soft Serve 0.8.1 Checksums")

@when("cosign is required")
def _(state: State):
    add_op(state,
       apk.packages,
       packages = ["cosign"]
    )

@when("Soft Serve checksums file is required")
def _(state: State):
    version: str = "0.8.1"
    add_op(state,
        files.download,
        name="Download Soft Serve Checksums",
        src=f"https://github.com/charmbracelet/soft-serve/releases/download/v{version}/checksums.txt",
        dest="/root/checksums.txt"
    )

    run_ops(state)

scenario("deploy.feature", "Require Soft Serve")

@when("Soft Serve is required")
def _(state: State, host: Host):
    version: str = "0.8.1"
    packages: dict = host.get_fact(ApkPackages)

    if "soft-serve" not in packages or packages["soft-serve"] != {version}:
        arch: str = host.get_fact(Arch)
        assert arch in ["aarch64", "armv7", "x86", "x86_64"] 

        pkg: str = f"soft-serve_{version}_{arch}.apk"

        add_op(state,
            files.download,
            name="Download Soft Serve Binary",
            src=f"https://github.com/charmbracelet/soft-serve/releases/download/v{version}/{pkg}",
            dest=f"/root/{pkg}"
        )

        add_op(
            state,
            server.shell,
            name="Install local APK with --allow-upgrades",
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

@then("Soft Serve is available")
def _(host: Host):
    enabled: dict = host.get_fact(OpenrcEnabled, "default")
    assert enabled['soft-serve'] is True
