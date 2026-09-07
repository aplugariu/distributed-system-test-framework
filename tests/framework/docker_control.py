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


def kill_container(container_name: str) -> None:
    subprocess.run(
        ["docker", "kill", container_name],
        check=True,
    )

def get_worker_containers() -> list[str]:
    result = subprocess.run(
        [
            "docker",
            "compose",
            "ps",
            "--format",
            "{{.Name}}",
            "worker",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]

def find_worker_processing_device(device_id: str) -> str:
    result = subprocess.run(
        ["docker", "compose", "logs", "worker"],
        capture_output=True,
        text=True,
        check=True,
    )

    for line in result.stdout.splitlines():
        if device_id in line and "event=processing_started" in line:
            return line.split("|")[0].strip()

    raise AssertionError(
        f"No worker found processing device {device_id}"
    )