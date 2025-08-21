## cuvette

a tiny wrapper around Beaker tooling. pairs well with [davidheineman/beaker_image](https://github.com/davidheineman/beaker_image).

### quick start

```sh
pip install cuvette
```

### demo

https://github.com/user-attachments/assets/4255e0be-b29d-40a0-ae9e-364ba7c9c446

**Also:** MacOS toolbar extension to show free GPUs, and currently running jobs! Instructions in [tools/macos_widget/README.md](tools/macos_widget/README.md)

<p align="center">
<img width="243" alt="demo-mac-plugin" src="https://github.com/user-attachments/assets/d648a0bb-b787-45f8-b5ac-7542eeb4a654" />
</p>

**features**

- Pre-installed VSCode/Cursor extensions on remote
- No saving API keys in plain-text in WEKA
- Auto-update `~/.ssh/config` SSH host (no manually entering `ssh phobos-cs-aus-452.reviz.ai2.in:32785` to connect to a host)
- Launch remote VSCode from terminal in one command (`ai2code your_folder`)
- GUI launcher (`bl`) with cluster descriptions (no fiddling with `beaker session create`)

### commands

`cuvette` is mainly a bag of terminal utilities:

```sh
bl # use interactive session launcher
bd # show current session
bdall # show all jobs
bstop # stop current session
blist # list current sessions
bport # change port for "ai2" host
ai2code . # launch remote code
ai2cursor . # launch remote cursor
ai2cleanup # run ai2 cleaning utils
blogs # get logs for job
bstream # stream logs for job
bcreate # create workspace
bsecrets # add secrets to workspace
bpriority # modify priority for all running experiments in a workspace
brestart # restart failed experiments in a workspace
```

<hr>

### migration todos

- [ ] `bcreate`
- [ ] `bsecrets`
- [ ] `bsecrets_davidh`
- [ ] `bsecretslist`
- [ ] A command to copy one secret from one workspace to another

### configuring secrets

```sh
# Make secrets files
touch secrets/.ssh/id_rsa # SSH private key (cat ~/.ssh/id_rsa)
touch secrets/.aws/credentials # AWS credentials (from 1password)
touch secrets/.aws/config # AWS config
touch secrets/.gcp/service-account.json # GCP service acct
touch secrets/.kaggle/kaggle.json # Kaggle acct

# Set secrets locally to add to Beaker
export HF_TOKEN=""
export OPENAI_API_KEY=""
export ANTHROPIC_API_KEY=""
export BEAKER_TOKEN=""
export WANDB_API_KEY=""
export COMET_API_KEY=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_ACCESS_KEY_ID=""
export GOOGLE_API_KEY=""
export WEKA_ENDPOINT_URL=""
export R2_ENDPOINT_URL=""
export SLACK_WEBHOOK_URL=""

# Create your workspace
bcreate ai2/davidh

# Copy secrets to workspace
bsecrets ai2/davidh
bsecrets_davidh ai2/davidh

# Sanity check (list all secrets)
bsecretslist ai2/davidh
```
