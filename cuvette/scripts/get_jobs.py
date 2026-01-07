import argparse
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from rich.console import Console
from rich.table import Table

from cuvette.utils.general import get_default_user
from cuvette.utils.poormansbeaker import JobClient, PoorMansBeaker


@dataclass
class ProcessedJob:
    workload: str | None
    id: str
    kind: Literal['session', 'execution']
    name: str
    start_date: datetime | None
    hostname: str
    priority: str | None
    port_mappings: dict | None
    gpus: str
    is_canceling: bool
    cuvette_port: int | None


def categorize_and_sort_jobs(jobs: list[ProcessedJob]) -> list[ProcessedJob]:
    """Sort jobs by date, with executions first, then sessions."""

    def sort_job_by_date(job: ProcessedJob):
        return job.start_date or ""

    queued_jobs = []
    executing_jobs = []
    queued_sessions = []
    executing_sessions = []

    for job in jobs:
        if job.kind == "Session":
            if job.start_date is None:
                queued_sessions.append(job)
            else:
                executing_sessions.append(job)
        else:
            if job.start_date is None:
                queued_jobs.append(job)
            else:
                executing_jobs.append(job)

    # Sort executing jobs/sessions by date
    executing_jobs.sort(key=sort_job_by_date)
    executing_sessions.sort(key=sort_job_by_date)

    return queued_jobs + executing_jobs + queued_sessions + executing_sessions


def list_workloads(
    username: str,
    sessions_only: bool = False,
    limit: int | None = 10,
) -> list[dict]:
    """gRPC is slow, so uses HTTPS for sessions+experiment data"""
    pmb = PoorMansBeaker.from_env()
    workloads = JobClient(beaker=pmb).list(
        author=username, 
        finalized=False, 
        limit=limit, 
        kind=("session" if sessions_only else None)
    )
    return workloads


def get_workload_details(job_id: str) -> dict:
    """Fetch detailed info for a single job (includes env_vars, port_mappings, etc.)"""
    pmb = PoorMansBeaker.from_env()
    return JobClient(beaker=pmb).get(job_id)


def parse_job_dict(job: dict) -> ProcessedJob:
    hostname = ""
    gpu_count = "0"
    cuvette_port = None

    # Find Env Vars
    env_vars = None
    if "session" in job and job["session"]:
        env_vars = job["session"].get("envVars") or job["session"].get("env_vars", [])
    elif "execution" in job and job["execution"]:
        # Compatible with classic job dict structure (fallback)
        spec = job["execution"].get("spec", {})
        env_vars = spec.get("envVars", []) or spec.get("env_vars", [])

    # Env Vars
    if env_vars is None:
        env_vars = []

    for env in env_vars:
        env_name = env.get("name") if isinstance(env, dict) else getattr(env, "name", None)
        env_value = env.get("value") if isinstance(env, dict) else getattr(env, "value", None)
        
        if env_name in ("BEAKER_HOSTNAME", "BEAKER_NODE_HOSTNAME") and env_value is not None:
            hostname = env_value
        elif env_name == "BEAKER_ASSIGNED_GPU_COUNT" and env_value is not None:
            gpu_count = env_value
        elif env_name == 'CUVETTE_PORT' and env_value is not None:
            try:
                cuvette_port = int(env_value)
            except (ValueError, TypeError):
                cuvette_port = None

    # Workload ID
    workload = None
    if "session" in job and job["session"]:
        session_env_vars = job["session"].get("envVars") or job["session"].get("env_vars", [])
        for env in session_env_vars:
            env_name = env.get("name") if isinstance(env, dict) else getattr(env, "name", None)
            env_value = env.get("value") if isinstance(env, dict) else getattr(env, "value", None)
            if env_name == "BEAKER_WORKLOAD_ID":
                workload = env_value
                break

    # Priority
    priority = None
    if "session" in job and job["session"]:
        priority = job["session"].get("priority", None)
    if priority is None and "execution" in job and job["execution"]:
        # Try to get from execution.spec.context.priority if available
        spec = job["execution"].get("spec", {})
        context = spec.get("context", {})
        priority = context.get("priority", None)

    # Start date
    start_date = None
    if "status" in job and job["status"]:
        start_date = job["status"].get("started", None)

    # Port mappings (API returns camelCase "portMappings")
    port_mappings = job.get("portMappings") or job.get("port_mappings", None)

    # Is canceling
    is_canceling = False
    if "status" in job and job["status"]:
        is_canceling = job["status"].get("canceled", None) is not None

    # Ensure start_date is datetime
    if start_date is not None and not isinstance(start_date, datetime):
        if isinstance(start_date, str):
            try:
                # Convert ISO string with possible Z
                start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            except Exception:
                start_date = None

    processed_job = ProcessedJob(
        workload=workload,
        id=job["id"],
        kind=job["kind"],
        name=job["name"],
        start_date=start_date,
        hostname=hostname,
        priority=priority,
        port_mappings=port_mappings,
        gpus=gpu_count,
        is_canceling=is_canceling,
        cuvette_port=cuvette_port
    )
    return processed_job


def get_job_data(username: str, sessions_only: bool = True) -> list[ProcessedJob]:
    jobs = list_workloads(
        username,
        # sessions_only=sessions_only,
        limit=None,
    )

    # Parse job data
    processed_jobs = []
    for job in jobs:
        processed_job = parse_job_dict(job)
        processed_jobs.append(processed_job)

    # Filter sessions by name or kind
    if sessions_only:
        processed_jobs = [
            job for job in processed_jobs if \
                job.name and 'cuvette' in job.name or 
                job.kind == 'session'
        ]

    processed_jobs = categorize_and_sort_jobs(processed_jobs)

    return processed_jobs


def display_jobs(author: str, include_experiments: bool):
    """Display jobs in a formatted table."""
    processed_jobs = get_job_data(username=author, sessions_only=not include_experiments)

    console = Console()
    table = Table(header_style="bold", box=None)

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Kind", style="magenta")
    table.add_column("Name", style="green")
    table.add_column("Start Date", style="white")
    table.add_column("Hostname", style="blue", overflow="fold")
    table.add_column("Priority", style="blue")
    table.add_column("GPUs", style="magenta")
    table.add_column("Ports", style="white")

    for job in processed_jobs:
        port_map_str = ""
        if job.port_mappings is not None:
            port_map_str = " ".join(f"{k}->{v}" for k, v in job.port_mappings.items())

        if job.is_canceling:
            continue  # Skip jobs being canceled

        if job.start_date is None:
            status_str = "[blue]Queued[/blue]"
        else:
            status_str = job.start_date.strftime("%Y-%m-%d %H:%M:%S")

        table.add_row(
            job.id,
            job.kind,
            job.name,
            status_str,
            job.hostname,
            job.priority,
            job.gpus,
            port_map_str,
        )

    console.print(table)


def sessions():
    """Entry point for listing sessions only."""
    parser = argparse.ArgumentParser(description="List all running sessions on AI2 through Beaker.")
    parser.add_argument(
        "--author", "-a", type=str, default=get_default_user(), help="The username to process."
    )
    args = parser.parse_args()

    display_jobs(args.author, include_experiments=False)


def all():
    """Entry point for listing all jobs (sessions and experiments)."""
    parser = argparse.ArgumentParser(
        description="List all running jobs on AI2 through Beaker (for cleaning up those you are done with)."
    )
    parser.add_argument(
        "--author", "-a", type=str, default=get_default_user(), help="The username to process."
    )
    args = parser.parse_args()

    display_jobs(args.author, include_experiments=True)


if __name__ == "__main__":
    all()
