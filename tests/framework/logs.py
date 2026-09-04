import subprocess


def get_service_logs(service_name: str) -> str:
    return subprocess.run(
        ["docker", "compose", "logs", service_name],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def get_trace(logs: str, correlation_id: str) -> str:
    return "\n".join(
        line
        for line in logs.splitlines()
        if correlation_id in line
    )