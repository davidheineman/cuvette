import time
from typing import List
from beaker import Beaker, Experiment
from beaker.exceptions import BeakerError

def beaker_experiment_failed(exp):
    """ Returns if beaker experiment failed. """
    if exp.jobs[0].execution.spec.replicas is not None:
        num_replicas = exp.jobs[0].execution.spec.replicas
    else:
        num_replicas = 1
        
    checks = []
    for job in exp.jobs:
        if job.status.exited is None:
            return False # at least one job is still running
        checks.append(job.status.finalized is not None and job.status.exit_code == 0)

    return sum(checks) != num_replicas


def gather_experiments(author_list, workspace_name, limit=2000):
    """ Gather all failed jobs """
    beaker = Beaker.from_env()
    experiments = []

    # Nice bookkeeping to see how many failed per author - a good gut check, if nothing else
    num_author_exps = {}
    for author in author_list:
        num_author_exps[author] = 0

    print(f'Pulling experiments from "{workspace_name}" for author(s) {author_list}...')
    exps = beaker.workspace.experiments(
        workspace=workspace_name, 
        limit=limit
    )
    
    for exp in exps:
        author = exp.author.name

        # filter by author and only collect failed experiments
        if author not in author_list or not beaker_experiment_failed(exp):
            continue

        experiments.append(exp)
        num_author_exps[author] += 1

    print (f"Total experiments that failed for authors {author_list}: {len(experiments)}")
    for author, count in num_author_exps.items():
        print(f"Author {author} had {count} failed experiments")
    return experiments


def restart_jobs(author, workspace, limit=5000):
    beaker = Beaker.from_env()
    experiments: List[Experiment] = gather_experiments(
        [author],
        workspace_name=workspace,
        limit=limit,
    )
    print(f"Found {len(experiments)} failed experiments")

    for i, experiment in enumerate(experiments):
        try:
            print(experiment.description)
            # beaker.experiment.resume(experiment)
        except BeakerError as e:
            print(f'Failed to restart https://beaker.org/ex/{experiment.id}: {e}')
            continue
        
        print(f"({i+1}/{len(experiments)}) Restarted https://beaker.org/ex/{experiment.id})")

        if (i + 1) % 200 == 0:
            print(f"Giving the Beaker API a 20s breather to prevent overloding and timeouts...")
            time.sleep(20)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--author", type=str, required=True, help="Author name to filter experiments by")
    parser.add_argument("-w", "--workspace", type=str, required=True, help="Beaker workspace name")
    parser.add_argument("-l", "--limit", type=int, default=5000, help="Maximum number of experiments to check")
    args = parser.parse_args()

    # python tools/scripts/restart_jobs.py -a davidh -w ai2/ladder-evals -l 5000

    restart_jobs(args.author, args.workspace, args.limit)