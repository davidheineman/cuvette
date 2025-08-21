# Relevant beaker scripts

BEAKER_TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
BEAKER_SECRETS_DIR="$(dirname "$BEAKER_TOOLS_DIR")/secrets"

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
