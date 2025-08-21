# Relevant beaker scripts

BEAKER_TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
BEAKER_SECRETS_DIR="$(dirname "$BEAKER_TOOLS_DIR")/secrets"

alias ai2="ssh ai2"
alias bs='beaker session stop'
alias bd='python '$BEAKER_TOOLS_DIR'/scripts/get_jobs.py --username davidh --sessions-only' # describe sessions
alias bdall='python '$BEAKER_TOOLS_DIR'/scripts/get_jobs.py --username davidh' # describe all jobs
alias bl='python '$BEAKER_TOOLS_DIR'/scripts/launcher.py' # launch session
alias blogs='python '$BEAKER_TOOLS_DIR'/scripts/stream_logs.py -j' # launch session
alias bstream='python '$BEAKER_TOOLS_DIR'/scripts/stream_logs.py -s -j' # launch session
alias blist='beaker session list --all --author davidh | grep running'
alias bport='source '$BEAKER_TOOLS_DIR'/update_port.sh' # update port to current session

brestart() {
    if [[ $# -lt 2 ]]; then
        echo "Usage: brestart <workspace> <limit>"
        return 1
    fi

    WORKSPACE="$1"
    LIMIT="$2"

    python $BEAKER_TOOLS_DIR/scripts/restart_jobs.py \
        --author davidh \
        --workspace $WORKSPACE \
        --limit $LIMIT
}

bstop() {
    if [[ $# -lt 2 ]]; then
        echo "Usage: bstop <workspace> <limit>"
        return 1
    fi

    WORKSPACE="$1"
    LIMIT="$2"

    python $BEAKER_TOOLS_DIR/scripts/stop_jobs.py \
        --author davidh \
        --workspace $WORKSPACE \
        --limit $LIMIT
}

bparse() {
    if [[ $# -lt 2 ]]; then
        echo "Usage: bparse <workspace> <limit> <prompt>"
        return 1
    fi

    WORKSPACE="$1"
    LIMIT="$2"
    PROMPT="$3"

    python $BEAKER_TOOLS_DIR/scripts/parse_logs_bulk.py \
        --author davidh \
        --workspace $WORKSPACE \
        --limit $LIMIT \
        --prompt $PROMPT
}

bpriority() {
    if [[ $# -lt 2 ]]; then
        echo "Usage: bpriority <workspace> <priority>"
        return 1
    fi

    WORKSPACE="$1"
    PRIORITY="$2"

    echo "Downloading current results for $WORKSPACE..."
    beaker workspace experiments "$WORKSPACE" --format json > /tmp/output.json
    JSON_FILE="/tmp/output.json"

    echo "Extracting BEAKER_JOB_IDs..."
    jq -r '.[] | .jobs[] | select(.status.canceledCode != 0 and .status.canceledCode != 1) | .id' "$JSON_FILE" | while read -r JOB_ID; do
        echo "Updating priority for job: $JOB_ID"
        beaker job update-priority "$JOB_ID" "$PRIORITY" --format json
    done
}

bcreate() {
    NEW_WORKSPACE_NAME="$1"
    NEW_WORKSPACE_NAME="${NEW_WORKSPACE_NAME#ai2/}" # Remove ai2/ prefix if it exists
    beaker workspace create "$NEW_WORKSPACE_NAME" -o ai2
    bsecrets ai2/$NEW_WORKSPACE_NAME
    bsecrets_davidh ai2/$NEW_WORKSPACE_NAME
}

bsecrets() { # add generic versions of keys
    WORKSPACE_NAME="$1"
    echo "Adding secrets to $WORKSPACE_NAME..."
    cat $BEAKER_SECRETS_DIR/.ssh/id_rsa | beaker secret write -w $WORKSPACE_NAME ssh-key
    cat $BEAKER_SECRETS_DIR/.aws/credentials | beaker secret write -w $WORKSPACE_NAME aws-creds
    cat $BEAKER_SECRETS_DIR/.aws/credentials | beaker secret write -w $WORKSPACE_NAME AWS_CREDENTIALS
    cat $BEAKER_SECRETS_DIR/.aws/config | beaker secret write -w $WORKSPACE_NAME aws-config
    cat $BEAKER_SECRETS_DIR/.aws/config | beaker secret write -w $WORKSPACE_NAME AWS_CONFIG
    cat $BEAKER_SECRETS_DIR/.gcp/service-account.json | beaker secret write -w $WORKSPACE_NAME gcp-creds
    cat $BEAKER_SECRETS_DIR/.kaggle/kaggle.json | beaker secret write -w $WORKSPACE_NAME kaggle-creds
    echo -n $HF_TOKEN | beaker secret write -w $WORKSPACE_NAME HF_TOKEN
    echo -n $HF_TOKEN | beaker secret write -w $WORKSPACE_NAME HF_TOKEN_READ_ONLY # <- for oe-eval
    echo -n $OPENAI_API_KEY | beaker secret write -w $WORKSPACE_NAME OPENAI_API_KEY
    echo -n $openai_api_key | beaker secret write -w $WORKSPACE_NAME openai_api_key
    echo -n $ANTHROPIC_API_KEY | beaker secret write -w $WORKSPACE_NAME ANTHROPIC_API_KEY
    echo -n $BEAKER_TOKEN | beaker secret write -w $WORKSPACE_NAME BEAKER_TOKEN
    echo -n $WANDB_API_KEY | beaker secret write -w $WORKSPACE_NAME WANDB_API_KEY
    echo -n $COMET_API_KEY | beaker secret write -w $WORKSPACE_NAME COMET_API_KEY
    echo -n $AWS_SECRET_ACCESS_KEY | beaker secret write -w $WORKSPACE_NAME AWS_SECRET_ACCESS_KEY
    echo -n $AWS_ACCESS_KEY_ID | beaker secret write -w $WORKSPACE_NAME AWS_ACCESS_KEY_ID
    echo -n $GOOGLE_API_KEY | beaker secret write -w $WORKSPACE_NAME GOOGLE_API_KEY
    echo -n $WEKA_ENDPOINT_URL | beaker secret write -w $WORKSPACE_NAME WEKA_ENDPOINT_URL
    echo -n $R2_ENDPOINT_URL | beaker secret write -w $WORKSPACE_NAME R2_ENDPOINT_URL
    echo -n $WEKA_PROFILE | beaker secret write -w $WORKSPACE_NAME WEKA_PROFILE
    echo -n $S3_PROFILE | beaker secret write -w $WORKSPACE_NAME S3_PROFILE
    echo -n $SLACK_WEBHOOK_URL | beaker secret write -w $WORKSPACE_NAME SLACK_WEBHOOK_URL
    echo -n $GITHUB_TOKEN | beaker secret write -w $WORKSPACE_NAME GITHUB_TOKEN
    echo -n $R2_SECRET_ACCESS_KEY | beaker secret write -w $WORKSPACE_NAME R2_SECRET_ACCESS_KEY
    echo -n $R2_ACCESS_KEY_ID | beaker secret write -w $WORKSPACE_NAME R2_ACCESS_KEY_ID
    echo -n $lambda_AWS_ACCESS_KEY_ID | beaker secret write -w $WORKSPACE_NAME lambda_AWS_ACCESS_KEY_ID
    echo -n $lambda_AWS_SECRET_ACCESS_KEY | beaker secret write -w $WORKSPACE_NAME lambda_AWS_SECRET_ACCESS_KEY
    beaker secret list -w $WORKSPACE_NAME
}

bsecrets_davidh() { # add davidh versions of keys
    WORKSPACE_NAME="$1"
    echo "Adding secrets to $WORKSPACE_NAME..."
    cat $BEAKER_SECRETS_DIR/.ssh/id_rsa | beaker secret write -w $WORKSPACE_NAME davidh-ssh-key
    cat $BEAKER_SECRETS_DIR/.aws/credentials | beaker secret write -w $WORKSPACE_NAME davidh-aws-creds
    cat $BEAKER_SECRETS_DIR/.aws/credentials | beaker secret write -w $WORKSPACE_NAME davidh_AWS_CREDENTIALS
    cat $BEAKER_SECRETS_DIR/.aws/config | beaker secret write -w $WORKSPACE_NAME davidh-aws-config
    cat $BEAKER_SECRETS_DIR/.aws/config | beaker secret write -w $WORKSPACE_NAME davidh_AWS_CONFIG
    cat $BEAKER_SECRETS_DIR/.gcp/service-account.json | beaker secret write -w $WORKSPACE_NAME davidh-gcp-creds
    cat $BEAKER_SECRETS_DIR/.kaggle/kaggle.json | beaker secret write -w $WORKSPACE_NAME davidh-kaggle-creds
    echo -n $HF_TOKEN | beaker secret write -w $WORKSPACE_NAME davidh_HF_TOKEN
    echo -n $HF_TOKEN | beaker secret write -w $WORKSPACE_NAME davidh_HF_TOKEN_READ_ONLY # <- for oe-eval
    echo -n $OPENAI_API_KEY | beaker secret write -w $WORKSPACE_NAME davidh_OPENAI_API_KEY
    echo -n $ANTHROPIC_API_KEY | beaker secret write -w $WORKSPACE_NAME davidh_ANTHROPIC_API_KEY
    echo -n $BEAKER_TOKEN | beaker secret write -w $WORKSPACE_NAME davidh_BEAKER_TOKEN
    echo -n $WANDB_API_KEY | beaker secret write -w $WORKSPACE_NAME davidh_WANDB_API_KEY
    echo -n $WANDB_API_KEY | beaker secret write -w $WORKSPACE_NAME DAVIDH_WANDB_API_KEY
    echo -n $COMET_API_KEY | beaker secret write -w $WORKSPACE_NAME davidh_COMET_API_KEY
    echo -n $COMET_API_KEY | beaker secret write -w $WORKSPACE_NAME DAVIDH_COMET_API_KEY
    echo -n $AWS_SECRET_ACCESS_KEY | beaker secret write -w $WORKSPACE_NAME davidh_AWS_SECRET_ACCESS_KEY
    echo -n $AWS_SECRET_ACCESS_KEY | beaker secret write -w $WORKSPACE_NAME DAVIDH_AWS_SECRET_ACCESS_KEY
    echo -n $AWS_ACCESS_KEY_ID | beaker secret write -w $WORKSPACE_NAME davidh_AWS_ACCESS_KEY_ID
    echo -n $AWS_ACCESS_KEY_ID | beaker secret write -w $WORKSPACE_NAME DAVIDH_AWS_ACCESS_KEY_ID
    echo -n $R2_SECRET_ACCESS_KEY | beaker secret write -w $WORKSPACE_NAME davidh_R2_SECRET_ACCESS_KEY
    echo -n $R2_SECRET_ACCESS_KEY | beaker secret write -w $WORKSPACE_NAME DAVIDH_R2_SECRET_ACCESS_KEY
    echo -n $R2_ACCESS_KEY_ID | beaker secret write -w $WORKSPACE_NAME davidh_R2_ACCESS_KEY_ID
    echo -n $R2_ACCESS_KEY_ID | beaker secret write -w $WORKSPACE_NAME DAVIDH_R2_ACCESS_KEY_ID
    echo -n $GOOGLE_API_KEY | beaker secret write -w $WORKSPACE_NAME davidh_GOOGLE_API_KEY
    echo -n $GITHUB_TOKEN | beaker secret write -w $WORKSPACE_NAME davidh_GITHUB_TOKEN
    echo -n $GITHUB_TOKEN | beaker secret write -w $WORKSPACE_NAME DAVIDH_GITHUB_TOKEN
    echo -n $lambda_AWS_ACCESS_KEY_ID | beaker secret write -w $WORKSPACE_NAME lambda_AWS_ACCESS_KEY_ID
    echo -n $lambda_AWS_SECRET_ACCESS_KEY | beaker secret write -w $WORKSPACE_NAME lambda_AWS_SECRET_ACCESS_KEY
    beaker secret list -w $WORKSPACE_NAME
}

bsecretslist() {
    WORKSPACE_NAME="$1"
    beaker secret list -w "$WORKSPACE_NAME" --format json | jq -r '.[].name' | while read -r SECRET_NAME; do
        echo -e "\n===== $SECRET_NAME ====="
        beaker secret read --workspace "$WORKSPACE_NAME" "$SECRET_NAME"
    done
}

bweb() {
    if [ -z "$*" ]; then
        open -a "Google Chrome" "https://beaker.allen.ai/orgs/ai2/workspaces/davidh?rowsPerPage=100"
    else
        open -a "Google Chrome" "https://beaker.allen.ai/orgs/ai2/workspaces/$*?rowsPerPage=100?"
    fi
}

bupdate() {
    chmod +x $BEAKER_TOOLS_DIR/download-beaker.sh
    source $BEAKER_TOOLS_DIR/download-beaker.sh
}

bfree() {
    python $BEAKER_TOOLS_DIR/get_free_gpus.py
}


# Pipe a gantry command into bstream. Usage: [gantry arg] | gstream
bfollow() {
  local id=$(grep -oE 'beaker.org/ex/01[A-Z0-9]{25}' | sed 's|.*/||')
  bstream "$id"
}


ai2code() {
    if [ -z "$1" ]; then
        code --remote ssh-remote+ai2 /root/ai2
    else
        local remote_path="${1:-}"
        code --remote ssh-remote+ai2 /root/ai2/$remote_path
    fi
}

ai2cursor() {
    if [ -z "$1" ]; then
        cursor --remote ssh-remote+ai2 /root/ai2
    else
        local remote_path="${1:-}"
        cursor --remote ssh-remote+ai2 /root/ai2/$remote_path
    fi
}

ai2codereset() {
    ai2 'rm -rf ~/.vscode-server/cli/servers'
}

ai2checks() {
    make type-check && make build && make style-check && make lint-check
}

ai2cleanup() {
    if [ "$1" = "--fix" ]; then
        isort . && black . && ruff check . --fix && mypy .
    else
        isort . && black . && ruff check . && mypy .
    fi
}