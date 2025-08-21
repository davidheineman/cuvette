import time
from typing import List
from beaker import Beaker, Experiment, Job
from beaker.exceptions import BeakerError

from cuvette.scripts.utils import gather_experiments, get_default_user


def change_priority(author, workspace, limit=5000):
    beaker = Beaker.from_env()
    experiments: List[Experiment] = gather_experiments(
        [author],
        workspace_name=workspace,
        limit=limit,
    )
    print(f"Found {len(experiments)} failed experiments")

    for i, experiment in enumerate(experiments):
        try:
            for job in experiment.jobs:
                job: Job
                # beaker job update-priority "$JOB_ID" "$PRIORITY" --format json
                raise NotImplementedError()
        except BeakerError as e:
            print(f'Failed to change priority https://beaker.org/ex/{experiment.id}: {e}')
            continue
        
        print(f"({i+1}/{len(experiments)}) updated https://beaker.org/ex/{experiment.id})")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--author', '-a', type=str, default=get_default_user(), help='Author name to filter experiments by.')
    parser.add_argument("-w", "--workspace", type=str, required=True, help="Beaker workspace name")
    parser.add_argument("-l", "--limit", type=int, default=100, help="Maximum number of experiments to check")
    args = parser.parse_args()

    change_priority(args.author, args.workspace, args.limit)