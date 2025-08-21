import argparse, warnings

# Suppress cryptography deprecation warnings
warnings.filterwarnings('ignore')

try:
    from beaker import Beaker
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beaker-py"])

from beaker import Beaker
from beaker.services.job import JobClient
from beaker.data_model.job import JobKind

# Attempt to install rich if it doesnt exist
try:
    import rich
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])

from rich.console import Console
from rich.table import Table


def parse_arguments():
    parser = argparse.ArgumentParser(description='Script to list all running jobs on AI2 through Beaker (for cleaning up those you are done with).')
    parser.add_argument('--username', '-u', type=str, required=True, help='The username to process.')
    parser.add_argument('--sessions-only', '-s', action='store_true', help='Only show interactive sessions.')
    return parser.parse_args()


def categorize_and_sort_jobs(jobs):
    """ Sort jobs by date, with excutions, then sessions. """
    def sort_job_by_date(job):
        return job["start_date"]

    queued_jobs = []
    executing_jobs = []
    queued_sessions = []
    executing_sessions = []

    for job in jobs:
        if job["kind"] == "Session":
            if job["start_date"] is None:
                queued_sessions.append(job)
            else:
                executing_sessions.append(job)
        else:
            if job["start_date"] is None:
                queued_jobs.append(job)
            else:
                executing_jobs.append(job)

    # Sort executing jobs/sessions by date
    executing_jobs.sort(key=sort_job_by_date)
    executing_sessions.sort(key=sort_job_by_date)

    return (
        queued_jobs +
        executing_jobs +
        queued_sessions +
        executing_sessions
    )


def get_job_data(username, sessions_only=True):
    beaker = Beaker.from_env()
    client = JobClient(beaker=beaker)

    jobs = client.list(
        kind=JobKind.session if sessions_only else None,
        author=username,
        finalized=False,
    )

    # Parse job data
    processed_jobs = []
    for job in jobs:
        hostname = ""
        gpu_count = "0"
        
        env_vars = job.session.env_vars if job.session else job.execution.spec.context.priority
        env_vars = env_vars or []
        for env in env_vars:
            if isinstance(env, str):
                continue
            if (env.name == "BEAKER_HOSTNAME" or env.name == "BEAKER_NODE_HOSTNAME") and env.value is not None:
                hostname = env.value
            elif env.name == "BEAKER_ASSIGNED_GPU_COUNT":
                gpu_count = env.value

        if job.execution:
            gpu_count = str(job.execution.spec.resources.gpu_count)

        workload = None
        if job.session and job.session.env_vars:
            for env in job.session.env_vars:
                if env.name == "BEAKER_WORKLOAD_ID":
                    workload = env.value
                    break

        priority = job.session.priority if job.session else job.execution.spec.context.priority
        
        processed_job = {
            "workload": workload,
            "id": job.id,
            "kind": job.kind,
            "name": job.name,
            "start_date": job.status.started,
            "hostname": hostname,
            "priority": priority,
            "port_mappings": job.port_mappings,
            "gpus": gpu_count,
            "is_canceling": job.status.canceled is not None
        }
        processed_jobs.append(processed_job)
    
    processed_jobs = categorize_and_sort_jobs(processed_jobs)

    return processed_jobs


def main():
    args = parse_arguments()

    processed_jobs = get_job_data(
        username=args.username, 
        sessions_only=args.sessions_only
    )

    console = Console()
    table = Table(header_style="bold", box=None)

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Kind", style="magenta")
    table.add_column("Name", style="green")
    table.add_column("Start Date", style="white")
    table.add_column("Hostname", style="blue", overflow="fold")
    table.add_column("Priority", style="blue")
    table.add_column("GPUs", style="magenta")
    table.add_column("Port Mappings", style="white")

    for job in processed_jobs:
        port_map_str = ""
        if job["port_mappings"] is not None:
            port_map_str = " ".join(f"{k}->{v}" for k, v in job["port_mappings"].items())
        
        if job["is_canceling"]:
            # status_str = "[red]Canceled[/red]"
            continue # just skip these
        elif job["start_date"] is None:
            status_str = "[blue]Queued[/blue]"
        else:
            status_str = job["start_date"].strftime("%Y-%m-%d %H:%M:%S")

        table.add_row(
            job["id"],
            job["kind"],
            job["name"],
            status_str,
            job["hostname"],
            job["priority"],
            job["gpus"],
            port_map_str,
        )

    console.print(table)

if __name__ == "__main__": main()