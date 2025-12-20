import argparse
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from beaker import Beaker
import beaker

SECRETS_ROOT = Path(__file__).parent.parent / "secrets"

GENERAL_FILE_SECRETS = [
    {"name": "ssh-key", "type": "file", "path": ".ssh/id_rsa"},
    {"name": "aws-creds", "type": "file", "path": ".aws/credentials"},
    {"name": "AWS_CREDENTIALS", "type": "file", "path": ".aws/credentials"},
    {"name": "aws-config", "type": "file", "path": ".aws/config"},
    {"name": "AWS_CONFIG", "type": "file", "path": ".aws/config"},
    {"name": "gcp-creds", "type": "file", "path": ".gcp/service-account.json"},
    {"name": "kaggle-creds", "type": "file", "path": ".kaggle/kaggle.json"},
]

GENERAL_ENV_SECRETS = [
    {"name": "HF_TOKEN", "type": "env", "env": "HF_TOKEN"},
    {"name": "HF_TOKEN_READ_ONLY", "type": "env", "env": "HF_TOKEN"},
    {"name": "OPENAI_API_KEY", "type": "env", "env": "OPENAI_API_KEY"},
    {"name": "openai_api_key", "type": "env", "env": "OPENAI_API_KEY"},
    {"name": "ANTHROPIC_API_KEY", "type": "env", "env": "ANTHROPIC_API_KEY"},
    {"name": "BEAKER_TOKEN", "type": "env", "env": "BEAKER_TOKEN"},
    {"name": "WANDB_API_KEY", "type": "env", "env": "WANDB_API_KEY"},
    {"name": "COMET_API_KEY", "type": "env", "env": "COMET_API_KEY"},
    {"name": "AWS_SECRET_ACCESS_KEY", "type": "env", "env": "AWS_SECRET_ACCESS_KEY"},
    {"name": "AWS_ACCESS_KEY_ID", "type": "env", "env": "AWS_ACCESS_KEY_ID"},
    {"name": "GOOGLE_API_KEY", "type": "env", "env": "GOOGLE_API_KEY"},
    {"name": "WEKA_ENDPOINT_URL", "type": "env", "env": "WEKA_ENDPOINT_URL"},
    {"name": "R2_ENDPOINT_URL", "type": "env", "env": "R2_ENDPOINT_URL"},
    {"name": "WEKA_PROFILE", "type": "env", "env": "WEKA_PROFILE"},
    {"name": "S3_PROFILE", "type": "env", "env": "S3_PROFILE"},
    {"name": "SLACK_WEBHOOK_URL", "type": "env", "env": "SLACK_WEBHOOK_URL"},
    {"name": "GITHUB_TOKEN", "type": "env", "env": "GITHUB_TOKEN"},
    {"name": "R2_SECRET_ACCESS_KEY", "type": "env", "env": "R2_SECRET_ACCESS_KEY"},
    {"name": "R2_ACCESS_KEY_ID", "type": "env", "env": "R2_ACCESS_KEY_ID"},
    {"name": "lambda_AWS_ACCESS_KEY_ID", "type": "env", "env": "lambda_AWS_ACCESS_KEY_ID"},
    {"name": "lambda_AWS_SECRET_ACCESS_KEY", "type": "env", "env": "lambda_AWS_SECRET_ACCESS_KEY"},
    {"name": "DOCKERHUB_USERNAME", "type": "env", "env": "DOCKERHUB_USERNAME"},
    {"name": "DOCKERHUB_TOKEN", "type": "env", "env": "DOCKERHUB_TOKEN"},
    {"name": "DOCENT_API_KEY", "type": "env", "env": "DOCENT_API_KEY"},
    {"name": "TINKER_API_KEY", "type": "env", "env": "TINKER_API_KEY"},
]


USER_FILE_SECRETS = [
    {"name": "davidh-ssh-key", "type": "file", "path": ".ssh/id_rsa"},
    {"name": "davidh-aws-creds", "type": "file", "path": ".aws/credentials"},
    {"name": "davidh_AWS_CREDENTIALS", "type": "file", "path": ".aws/credentials"},
    {"name": "davidh-aws-config", "type": "file", "path": ".aws/config"},
    {"name": "davidh_AWS_CONFIG", "type": "file", "path": ".aws/config"},
    {"name": "davidh-gcp-creds", "type": "file", "path": ".gcp/service-account.json"},
    {"name": "davidh-kaggle-creds", "type": "file", "path": ".kaggle/kaggle.json"},
]


USER_ENV_SECRETS = [
    {"name": "davidh_HF_TOKEN", "type": "env", "env": "HF_TOKEN"},
    {"name": "davidh_HF_TOKEN_READ_ONLY", "type": "env", "env": "HF_TOKEN"},
    {"name": "davidh_OPENAI_API_KEY", "type": "env", "env": "OPENAI_API_KEY"},
    {"name": "davidh_ANTHROPIC_API_KEY", "type": "env", "env": "ANTHROPIC_API_KEY"},
    {"name": "davidh_BEAKER_TOKEN", "type": "env", "env": "BEAKER_TOKEN"},
    {"name": "davidh_WANDB_API_KEY", "type": "env", "env": "WANDB_API_KEY"},
    {"name": "DAVIDH_WANDB_API_KEY", "type": "env", "env": "WANDB_API_KEY"},
    {"name": "davidh_COMET_API_KEY", "type": "env", "env": "COMET_API_KEY"},
    {"name": "DAVIDH_COMET_API_KEY", "type": "env", "env": "COMET_API_KEY"},
    {"name": "davidh_AWS_SECRET_ACCESS_KEY", "type": "env", "env": "AWS_SECRET_ACCESS_KEY"},
    {"name": "DAVIDH_AWS_SECRET_ACCESS_KEY", "type": "env", "env": "AWS_SECRET_ACCESS_KEY"},
    {"name": "davidh_AWS_ACCESS_KEY_ID", "type": "env", "env": "AWS_ACCESS_KEY_ID"},
    {"name": "DAVIDH_AWS_ACCESS_KEY_ID", "type": "env", "env": "AWS_ACCESS_KEY_ID"},
    {"name": "davidh_R2_SECRET_ACCESS_KEY", "type": "env", "env": "R2_SECRET_ACCESS_KEY"},
    {"name": "DAVIDH_R2_SECRET_ACCESS_KEY", "type": "env", "env": "R2_SECRET_ACCESS_KEY"},
    {"name": "davidh_R2_ACCESS_KEY_ID", "type": "env", "env": "R2_ACCESS_KEY_ID"},
    {"name": "DAVIDH_R2_ACCESS_KEY_ID", "type": "env", "env": "R2_ACCESS_KEY_ID"},
    {"name": "davidh_GOOGLE_API_KEY", "type": "env", "env": "GOOGLE_API_KEY"},
    {"name": "davidh_GITHUB_TOKEN", "type": "env", "env": "GITHUB_TOKEN"},
    {"name": "DAVIDH_GITHUB_TOKEN", "type": "env", "env": "GITHUB_TOKEN"},
    {"name": "lambda_AWS_ACCESS_KEY_ID", "type": "env", "env": "lambda_AWS_ACCESS_KEY_ID"},
    {"name": "lambda_AWS_SECRET_ACCESS_KEY", "type": "env", "env": "lambda_AWS_SECRET_ACCESS_KEY"},
    {"name": "davidh_DOCKERHUB_USERNAME", "type": "env", "env": "DOCKERHUB_USERNAME"},
    {"name": "DAVIDH_DOCKERHUB_USERNAME", "type": "env", "env": "DOCKERHUB_USERNAME"},
    {"name": "davidh_DOCKERHUB_TOKEN", "type": "env", "env": "DOCKERHUB_TOKEN"},
    {"name": "DAVIDH_DOCKERHUB_TOKEN", "type": "env", "env": "DOCKERHUB_TOKEN"},
    {"name": "davidh_DOCENT_API_KEY", "type": "env", "env": "DOCENT_API_KEY"},
    {"name": "DAVIDH_DOCENT_API_KEY", "type": "env", "env": "DOCENT_API_KEY"},
    {"name": "davidh_TINKER_API_KEY", "type": "env", "env": "TINKER_API_KEY"},
    {"name": "DAVIDH_TINKER_API_KEY", "type": "env", "env": "TINKER_API_KEY"},
]


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
    except beaker.exceptions.BeakerPermissionsError as e:
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
    args = parser.parse_args()

    workspace_name = args.workspace

    beaker = Beaker.from_env()
    # Get workspace object first
    workspace = beaker.workspace.get(workspace_name)
    secrets = beaker.secret.list(workspace=workspace)

    for secret in secrets:
        print(secret.name)

        if args.show_values:
            value = beaker.secret.read(secret, workspace=workspace)
            print(value)


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
        # Read the secret from the source workspace
        secret_value = beaker.secret.read(args.secret, workspace=args.from_workspace)
        
        # Determine the name for the secret in the destination workspace
        destination_name = args.new_name if args.new_name else args.secret
        
        # Write the secret to the destination workspace
        beaker.secret.write(destination_name, secret_value, workspace=args.to_workspace)
        
        print(f"Copied '{args.secret}': '{args.from_workspace}' -> '{args.to_workspace}' ('{destination_name}')")
        
    except Exception as e:
        print(f"Error copying secret: {e}")
