import time
from beaker import Beaker
from beaker.exceptions import BeakerError

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
        if author not in author_list:
            continue

        experiments.append(exp)
        num_author_exps[author] += 1

    print (f"Total experiments that failed for authors {author_list}: {len(experiments)}")
    for author, count in num_author_exps.items():
        print(f"Author {author} had {count} failed experiments")
    return experiments


def delete_jobs(term, author, workspace, limit=5000):
    beaker = Beaker.from_env()
    experiments = gather_experiments(
        [author],
        workspace_name=workspace,
        limit=limit,
    )
    print(f"Found {len(experiments)} failed experiments")

    num_deleted = 0
    for i, experiment in enumerate(experiments):
        if term in experiment.name:
            try:
                beaker.experiment.delete(experiment)
                num_deleted += 1
            except BeakerError as e:
                print(f'Failed to delete https://beaker.org/ex/{experiment.id}: {e}')
                continue
        
            print(f"({i+1}/{len(experiments)}) Deleted '{experiment.name}' (https://beaker.org/ex/{experiment.id})")

        if (num_deleted + 1) % 200 == 0:
            print(f"Giving the Beaker API a 20s breather to prevent overloding and timeouts...")
            time.sleep(20)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--term", type=str, required=True, help="A term in the experiment name to use for deletion")
    parser.add_argument("-a", "--author", type=str, required=True, help="Author name to filter experiments by")
    parser.add_argument("-w", "--workspace", type=str, required=True, help="Beaker workspace name")
    parser.add_argument("-l", "--limit", type=int, default=5000, help="Maximum number of experiments to check")
    args = parser.parse_args()

    delete_jobs(args.term, args.author, args.workspace, args.limit)