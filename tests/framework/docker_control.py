import subprocess


def stop_service(service_name: str) -> None:
    subprocess.run(
        ["docker", "compose", "stop", service_name],
        check=True,
    )


def start_service(service_name: str) -> None:
    subprocess.run(
        ["docker", "compose", "start", service_name],
        check=True,
    )


def kill_service(service_name: str) -> None:
    subprocess.run(
        ["docker", "compose", "kill", service_name],
        check=True,
    )