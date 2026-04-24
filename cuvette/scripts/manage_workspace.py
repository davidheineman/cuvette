import argparse
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from beaker import Beaker
from beaker.exceptions import BeakerPermissionsError

from cuvette.constants.secrets import GENERAL_ENV_SECRETS, GENERAL_FILE_SECRETS, SECRETS_ROOT, USER_ENV_SECRETS, USER_FILE_SECRETS


def create_workspace(name, description=None, public=True):
    beaker = Beaker.from_env()
    
    workspace = beaker.workspace.create(
        name,
        description=description
    )
    
    return workspace


def create():
    parser = argparse.ArgumentParser(
        description="Create a workspace."
    )
    parser.add_argument(
        "-w", "--workspace", type=str, help="Name of the workspace to create."
    )
    args = parser.parse_args()

    workspace = create_workspace(args.workspace)
    
    workspace_suffix = args.workspace.split('/')[-1] # ai2/davidh -> davidh

    print(f"Created: https://beaker.allen.ai/orgs/ai2/workspaces/{workspace_suffix}")


def _sync_secret(bk, workspace_name, entry):
    secret_name = entry['name']
    type = entry['type']
    env = entry.get('env', None)
    path = entry.get('path', None)

    if type == 'env':
        # Read from environment variable
        value = os.environ.get(env)
        if value is None:
            print(f"Warning: Environment variable {env} not found")
            return
    elif type == "file":
        full_path = SECRETS_ROOT / Path(path)

        # Read from file
        try:
            with open(full_path, 'r') as f:
                value = f.read()
        except FileNotFoundError:
            print(f"Warning: File {path} not found")
            return
    else:
        print(f"Warning: Invalid source for secret {secret_name}")
        return

    # remove leading / trailing spaces or newlines
    value = value.strip()
    
    # Write secret to workspace
    try:
        bk.secret.write(
            secret_name,
            value,
            workspace=workspace_name
        )
        print(f"Added: {secret_name}")
    except BeakerPermissionsError as e:
        print(f"\033[31mFailed: {secret_name} ({e})\033[0m")


def sync_secrets(workspace_name, secrets_config):
    beaker = Beaker.from_env()
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for entry in secrets_config:
            future = executor.submit(_sync_secret, beaker, workspace_name, entry)
            futures.append(future)
        
        # Wait for all tasks to complete
        for future in futures:
            future.result()


def sync():
    parser = argparse.ArgumentParser(
        description="Sync secrets to a Beaker workspace."
    )
    parser.add_argument(
        "--workspace", "-w", type=str, required=True, help="The name of the workspace."
    )
    parser.add_argument(
        "--all", "-a", action="store_true", help="Sync both general and user secrets."
    )
    args = parser.parse_args()
    
    if args.all:
        sync_secrets(args.workspace, GENERAL_FILE_SECRETS + GENERAL_ENV_SECRETS + USER_FILE_SECRETS + USER_ENV_SECRETS)
    else:
        sync_secrets(args.workspace, USER_FILE_SECRETS + USER_ENV_SECRETS)


def list_secrets():
    parser = argparse.ArgumentParser(
        description="List secrets in a Beaker workspace."
    )
    parser.add_argument(
        "--workspace", "-w", type=str, required=True, help="The name of the workspace."
    )
    parser.add_argument(
        "--show_values", "-v", action="store_true", help="Show all values."
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Output as JSON (implies -v)."
    )
    args = parser.parse_args()

    workspace_name = args.workspace

    beaker = Beaker.from_env()
    workspace = beaker.workspace.get(workspace_name)
    secrets = beaker.secret.list(workspace=workspace)

    if args.json or args.show_values:
        def _read(secret):
            return secret.name, beaker.secret.read(secret, workspace=workspace)

        with ThreadPoolExecutor(max_workers=32) as executor:
            result = dict(executor.map(_read, secrets))

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for name, value in result.items():
                print(name)
                print(value)
    else:
        for secret in secrets:
            print(secret.name)


def copy_secret():
    parser = argparse.ArgumentParser(
        description="Copy a secret from one Beaker workspace to another."
    )
    parser.add_argument(
        "--from-workspace", "-f", type=str, required=True, help="The source workspace."
    )
    parser.add_argument(
        "--to-workspace", "-t", type=str, required=True, help="The destination workspace."
    )
    parser.add_argument(
        "--secret", "-s", type=str, required=True, help="The name of the secret to copy."
    )
    parser.add_argument(
        "--new-name", "-n", type=str, help="New name for the secret in destination workspace (optional)."
    )
    args = parser.parse_args()

    beaker = Beaker.from_env()
    
    try:
        # Get workspace objects
        from_workspace = beaker.workspace.get(args.from_workspace)
        to_workspace = beaker.workspace.get(args.to_workspace)
        
        # Get the secret object from the source workspace
        secret = beaker.secret.get(args.secret, workspace=from_workspace)
        
        # Read the secret value
        secret_value = beaker.secret.read(secret, workspace=from_workspace)
        
        # Determine the name for the secret in the destination workspace
        destination_name = args.new_name if args.new_name else args.secret
        
        # Write the secret to the destination workspace
        beaker.secret.write(destination_name, secret_value, workspace=to_workspace)
        
        print(f"Copied '{args.secret}': '{args.from_workspace}' -> '{args.to_workspace}' ('{destination_name}')")
        
    except Exception as e:
        print(f"Error copying secret '{args.secret}': {type(e).__name__}: {e}")


def archive():
    parser = argparse.ArgumentParser(
        description="Archive (remove) one or more Beaker workspaces."
    )
    parser.add_argument(
        "workspaces", nargs="+", type=str, help="Names of the workspaces to archive."
    )
    parser.add_argument(
        "--unarchive", "-u", action="store_true", help="Unarchive instead of archive."
    )
    args = parser.parse_args()

    beaker = Beaker.from_env()
    action = "Unarchiving" if args.unarchive else "Archiving"
    archived = not args.unarchive

    for workspace_name in args.workspaces:
        try:
            workspace = beaker.workspace.get(workspace_name)
            beaker.workspace.update(workspace, archived=archived)
            print(f"{action}: {workspace_name}")
        except Exception as e:
            print(f"\033[31mFailed to update {workspace_name}: {type(e).__name__}: {e}\033[0m")


def _delete_secrets(workspace_name, filter_fn=None, dry_run=False, beaker=None):
    """Delete secrets from a workspace. If filter_fn is None, deletes all."""
    if beaker is None:
        beaker = Beaker.from_env()
    print(f"Scanning {workspace_name}...", flush=True)
    workspace = beaker.workspace.get(workspace_name)
    secrets = list(beaker.secret.list(workspace=workspace))

    if filter_fn:
        targets = [s for s in secrets if filter_fn(s)]
    else:
        targets = secrets

    if not targets:
        print(f"{workspace_name}: no matching secrets found.")
        return 0

    prefix = "[DRY RUN] " if dry_run else ""
    print(f"{prefix}{workspace_name}: {len(targets)} secret(s) to delete")

    for secret in targets:
        print(f"  {prefix}{secret.name}")

    if dry_run:
        return 0

    deleted = 0
    failed = 0

    def _do_delete(secret):
        beaker.secret.delete(secret, workspace=workspace)
        return secret.name

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(_do_delete, s): s for s in targets}
        for future in as_completed(futures):
            secret = futures[future]
            try:
                future.result()
                deleted += 1
            except Exception as e:
                failed += 1
                print(f"  \033[31mFailed to delete {secret.name}: {e}\033[0m")

    print(f"Deleted {deleted}/{len(targets)} secret(s) from {workspace_name}.")
    return deleted


def _collect_workspaces(args):
    """Gather workspace names from positional args and --file, optionally limited to first N."""
    workspaces = list(args.workspaces or [])
    if args.file:
        with open(args.file, 'r') as f:
            workspaces.extend(line.strip() for line in f if line.strip())
    if not workspaces:
        print("No workspaces specified. Use positional args or --file.")
        return workspaces
    if hasattr(args, 'n') and args.n is not None:
        workspaces = workspaces[:args.n]
    return workspaces


def purge_secrets():
    parser = argparse.ArgumentParser(
        description="Delete ALL secrets from a Beaker workspace."
    )
    parser.add_argument(
        "workspaces", nargs="*", type=str, help="Workspaces to purge."
    )
    parser.add_argument(
        "--file", "-f", type=str, help="File with workspace names (one per line)."
    )
    parser.add_argument(
        "-n", type=int, default=None, help="Only process the first N workspaces."
    )
    parser.add_argument(
        "--dry-run", "-d", action="store_true", help="Print what would be deleted without deleting."
    )
    parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt."
    )
    args = parser.parse_args()

    workspaces = _collect_workspaces(args)
    if not workspaces:
        return

    if not args.dry_run and not args.yes:
        resp = input(f"Delete ALL secrets from {len(workspaces)} workspace(s)? [y/N] ")
        if resp.lower() != "y":
            print("Aborted.")
            return

    beaker = Beaker.from_env()
    for ws in workspaces:
        try:
            _delete_secrets(ws, filter_fn=None, dry_run=args.dry_run, beaker=beaker)
        except Exception as e:
            print(f"\033[31m{ws}: {type(e).__name__}: {e}\033[0m")


def delete_user_secrets():
    parser = argparse.ArgumentParser(
        description="Delete secrets containing 'davidh' or 'DAVIDH' from Beaker workspaces."
    )
    parser.add_argument(
        "workspaces", nargs="*", type=str, help="Workspaces to clean."
    )
    parser.add_argument(
        "--file", "-f", type=str, help="File with workspace names (one per line)."
    )
    parser.add_argument(
        "-n", type=int, default=None, help="Only process the first N workspaces."
    )
    parser.add_argument(
        "--patterns", "-p", nargs="+", type=str, default=["davidh", "DAVIDH"],
        help="Substrings to match in secret names. Default: davidh DAVIDH"
    )
    parser.add_argument(
        "--dry-run", "-d", action="store_true", help="Print what would be deleted without deleting."
    )
    args = parser.parse_args()

    workspaces = _collect_workspaces(args)
    if not workspaces:
        return

    filter_fn = lambda s: any(pat in s.name for pat in args.patterns)

    beaker = Beaker.from_env()
    for ws in workspaces:
        try:
            _delete_secrets(ws, filter_fn=filter_fn, dry_run=args.dry_run, beaker=beaker)
        except Exception as e:
            print(f"\033[31m{ws}: {type(e).__name__}: {e}\033[0m")


def _load_local_secret_values():
    """Load all known secret values from local env vars and secret files."""
    all_secrets = GENERAL_ENV_SECRETS + GENERAL_FILE_SECRETS + USER_ENV_SECRETS + USER_FILE_SECRETS
    values = set()
    loaded_env = 0
    loaded_file = 0

    seen_env = set()
    seen_file = set()

    for entry in all_secrets:
        if entry["type"] == "env":
            env_var = entry["env"]
            if env_var in seen_env:
                continue
            seen_env.add(env_var)
            val = os.environ.get(env_var)
            if val and val.strip():
                values.add(val.strip())
                loaded_env += 1
        elif entry["type"] == "file":
            path = entry["path"]
            if path in seen_file:
                continue
            seen_file.add(path)
            full_path = SECRETS_ROOT / Path(path)
            try:
                with open(full_path, 'r') as f:
                    val = f.read().strip()
                    if val:
                        values.add(val)
                        loaded_file += 1
            except FileNotFoundError:
                pass

    print(f"Loaded {len(values)} unique secret values ({loaded_env} env vars, {loaded_file} files).")
    return values


def delete_by_value():
    parser = argparse.ArgumentParser(
        description="Delete secrets whose VALUES match your local env vars / secret files."
    )
    parser.add_argument(
        "workspaces", nargs="*", type=str, help="Workspaces to scan."
    )
    parser.add_argument(
        "--file", "-f", type=str, help="File with workspace names (one per line)."
    )
    parser.add_argument(
        "-n", type=int, default=None, help="Only process the first N workspaces."
    )
    parser.add_argument(
        "--dry-run", "-d", action="store_true", help="Print what would be deleted without deleting."
    )
    args = parser.parse_args()

    workspaces = _collect_workspaces(args)
    if not workspaces:
        return

    known_values = _load_local_secret_values()
    if not known_values:
        print("No local secret values found. Nothing to match against.")
        return

    beaker = Beaker.from_env()
    total_deleted = 0

    for ws_name in workspaces:
        try:
            workspace = beaker.workspace.get(ws_name)
            secrets = list(beaker.secret.list(workspace=workspace))
        except Exception as e:
            print(f"\033[31m{ws_name}: {e}\033[0m")
            continue

        if not secrets:
            continue

        def _read_secret(secret):
            try:
                val = beaker.secret.read(secret, workspace=workspace)
                return secret, val.strip()
            except Exception:
                return secret, None

        matched = []
        with ThreadPoolExecutor(max_workers=16) as executor:
            for secret, val in executor.map(_read_secret, secrets):
                if val is not None and val in known_values:
                    matched.append(secret)

        if not matched:
            continue

        prefix = "[DRY RUN] " if args.dry_run else ""
        print(f"{prefix}{ws_name}: {len(matched)} secret(s) to delete")
        for secret in matched:
            print(f"  {prefix}{secret.name}")

        if not args.dry_run:
            def _do_delete(secret):
                beaker.secret.delete(secret, workspace=workspace)

            deleted = 0
            with ThreadPoolExecutor(max_workers=16) as executor:
                futures = {executor.submit(_do_delete, s): s for s in matched}
                for future in as_completed(futures):
                    s = futures[future]
                    try:
                        future.result()
                        deleted += 1
                    except Exception as e:
                        print(f"  \033[31mFailed to delete {s.name}: {e}\033[0m")

            print(f"  Deleted {deleted}/{len(matched)}.")
            total_deleted += deleted

    if args.dry_run:
        print(f"\nDry run complete. No secrets were deleted.")
    else:
        print(f"\nDone. Deleted {total_deleted} secret(s) total.")


def clean_secrets():
    parser = argparse.ArgumentParser(
        description="Traverse workspaces and delete secrets matching name patterns or value lists."
    )
    parser.add_argument(
        "--workspaces", "-w", nargs="+", type=str,
        help="Workspaces to scan. If not provided, scans all workspaces in the org."
    )
    parser.add_argument(
        "--name-patterns", "-n", nargs="+", type=str, default=["davidh", "DAVIDH"],
        help="Delete secrets whose names contain any of these substrings (case-sensitive). "
             "Default: davidh DAVIDH"
    )
    parser.add_argument(
        "--match-values-file", "-f", type=str,
        help="Path to a file with values to match against (one per line). "
             "Secrets whose values match any line will be deleted."
    )
    parser.add_argument(
        "--match-values", "-m", nargs="+", type=str,
        help="Values to match against. Secrets whose values match any of these will be deleted."
    )
    parser.add_argument(
        "--dry-run", "-d", action="store_true",
        help="Print what would be deleted without actually deleting."
    )
    parser.add_argument(
        "--read-values", "-r", action="store_true",
        help="Also read secret values to match against --match-values / --match-values-file. "
             "Off by default (name matching only) since reading values is slow."
    )
    args = parser.parse_args()

    match_values = set()
    if args.match_values:
        match_values.update(v.strip() for v in args.match_values)
    if args.match_values_file:
        with open(args.match_values_file, 'r') as f:
            match_values.update(line.strip() for line in f if line.strip())

    if match_values and not args.read_values:
        args.read_values = True
        print("Note: --read-values enabled automatically since match values were provided.\n")

    beaker = Beaker.from_env()

    if args.workspaces:
        workspaces = []
        for name in args.workspaces:
            try:
                workspaces.append(beaker.workspace.get(name))
            except Exception as e:
                print(f"\033[31mSkipping {name}: {e}\033[0m")
    else:
        print("Listing all workspaces in org...")
        workspaces = list(beaker.workspace.list())
        print(f"Found {len(workspaces)} workspaces.\n")

    total_deleted = 0

    for workspace in workspaces:
        try:
            secrets = list(beaker.secret.list(workspace=workspace))
        except Exception as e:
            print(f"\033[31mCannot list secrets in {workspace.name}: {e}\033[0m")
            continue

        name_matched = []
        remaining = []
        for secret in secrets:
            if any(pat in secret.name for pat in args.name_patterns):
                name_matched.append(secret)
            else:
                remaining.append(secret)

        value_matched = []
        if args.read_values and match_values and remaining:
            def _check_value(secret):
                try:
                    val = beaker.secret.read(secret, workspace=workspace)
                    if val.strip() in match_values:
                        return secret
                except Exception:
                    pass
                return None

            with ThreadPoolExecutor(max_workers=16) as executor:
                futures = {executor.submit(_check_value, s): s for s in remaining}
                for future in as_completed(futures):
                    result = future.result()
                    if result is not None:
                        value_matched.append(result)

        to_delete = name_matched + value_matched
        if not to_delete:
            continue

        prefix = "[DRY RUN] " if args.dry_run else ""
        print(f"{prefix}{workspace.name}: {len(to_delete)} secret(s) to delete")
        for secret in name_matched:
            print(f"  {prefix}(name match) {secret.name}")
        for secret in value_matched:
            print(f"  {prefix}(value match) {secret.name}")

        if not args.dry_run:
            for secret in to_delete:
                try:
                    beaker.secret.delete(secret, workspace=workspace)
                except Exception as e:
                    print(f"  \033[31mFailed to delete {secret.name}: {e}\033[0m")
            total_deleted += len(to_delete)

    if args.dry_run:
        print(f"\nDry run complete. No secrets were deleted.")
    else:
        print(f"\nDone. Deleted {total_deleted} secret(s) total.")
