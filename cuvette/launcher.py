import argparse
import curses
import os
import re
import subprocess
import sys
import time
from typing import Optional

from cuvette.warning_utils import setup_cuvette_warnings
from cuvette.secrets import USER_ENV_SECRETS, USER_FILE_SECRETS
from cuvette.gui import ClusterSelector

setup_cuvette_warnings()

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SESSION_NAME = "👋davidh👋"

SESSION_NAME = "eval-debugging"
SESSION_WORKSPACE = "ai2/olmo-3-evals"
SESSION_PRIORITY = "high"

LAUNCH_COMMAND = """\
beaker session create \
    --name {name} \
    {gpu_command} \
    {cluster_command} \
    {hostname_command} \
    --image beaker://davidh/davidh-interactive \
    --workspace {workspace} \
    --priority {priority} \
    --budget ai2/oe-base \
    --bare \
    --detach \
    --port 8000 --port 8001 --port 8080 --port 8888 \
    --workdir /oe-eval-default/davidh \
    --mount src=weka,ref=oe-eval-default,dst=/oe-eval-default \
    --mount src=weka,ref=oe-training-default,dst=/oe-training-default \
    --mount src=weka,ref=oe-adapt-default,dst=/oe-adapt-default \
    {user_file_secrets} \
    {user_env_secrets} \
    -- /entrypoint.sh\
"""

UPDATE_PORT_CMD = "bport {session_id}"


def send_notification(title, message):
    """Send a notification on MacOS"""
    os.system(f"""osascript -e 'display notification "{message}" with title "{title}"' """)


def get_host_name(session_id):
    """Get the hostname for a session ID"""
    command = ["beaker", "session", "describe"]
    if session_id:
        command.append(session_id)

    result = subprocess.run(command, capture_output=True, text=True)

    match = re.search(r"[^\s]*\.reviz\.ai2\.in", result.stdout)

    return match.group(0) if match else None


def build_launch_command(
    cluster_name: Optional[str | list] = None,
    host_name: Optional[str | list] = None,
    num_gpus: int = 0,
    session_name: str = SESSION_NAME,
    workspace: str = SESSION_WORKSPACE,
    priority: str = SESSION_PRIORITY,
) -> str:
    """Build the beaker session launch command"""
    gpu_command = ""
    if num_gpus > 0:
        gpu_command = f"--gpus {num_gpus}"

    cluster_command = ""
    if cluster_name is not None:
        if not isinstance(cluster_name, list):
            cluster_name = [cluster_name]
        for _cluster_name in cluster_name:
            cluster_command += f"--cluster {_cluster_name} "

    hostname_command = ""
    if host_name is not None:
        if not isinstance(host_name, list):
            host_name = [host_name]
        for _host_name in host_name:
            hostname_command += f"--hostname {_host_name} "

    user_file_secrets_str = ""
    dst_seen = set()
    for user_file_secret in USER_FILE_SECRETS:
        ref, dst = user_file_secret['name'], f"/root/{user_file_secret['path']}"
        
        # No duplicate destinations for mounts. Only keep the first
        if dst in dst_seen:
            continue
        dst_seen.add(dst)
        
        user_file_secrets_str += f"--mount src=secret,ref={ref},dst={dst} "
    
    user_env_secrets_str = ""
    for user_env_secret in USER_ENV_SECRETS:
        local_name, beaker_name = user_env_secret['env'], user_env_secret['name']
        user_env_secrets_str += f"--secret-env {local_name}={beaker_name} "

    command = LAUNCH_COMMAND.format(
        name=session_name,
        workspace=workspace,
        priority=priority,
        gpu_command=gpu_command,
        cluster_command=cluster_command,
        hostname_command=hostname_command,
        user_file_secrets=user_file_secrets_str,
        user_env_secrets=user_env_secrets_str,
    )
    command = command.replace("  ", " ")
    return command


def extract_session_id(output_lines: list[str]) -> Optional[str]:
    """Extract session ID from output lines"""
    for line in output_lines:
        if "Starting session" in line:
            return line.split()[2]  # Gets the session ID from "Starting session {id} ..."
    return None


def handle_session_completion(returncode: int, output_lines: list[str], session_id: str) -> tuple[Optional[str], bool]:
    """Handle session launch completion and port update"""
    try:
        # Get the hostname for printing
        host_name = get_host_name(session_id)

        # Wait 1 second before connecting (or else the locking mechanism fails)
        time.sleep(2)

        # Run the port update script
        port_process = subprocess.run(
            UPDATE_PORT_CMD.format(session_id=session_id),
            shell=True,
            executable="/bin/zsh",
            capture_output=True,
            text=True,
        )

        if port_process.returncode == 0:
            # Extract num_gpus from output_lines if needed for notification
            num_gpus = 0
            for line in output_lines:
                if "--gpus" in line:
                    try:
                        num_gpus = int(line.split("--gpus")[1].split()[0])
                        break
                    except (IndexError, ValueError):
                        pass
            
            updated_notif = f"Session launched with {num_gpus} GPUs on {host_name}"
            send_notification("Beaker Launch", updated_notif)
            return host_name, True
        else:
            error_notif = f"Port update failed ({session_id})"
            send_notification("Beaker Launch", error_notif)
            return host_name, False
    except Exception as e:
        error_notif = f"Port update error: {str(e)}"
        send_notification("Beaker Launch", error_notif)
        return None, False


def build_quick_start_command(
    cluster_name: Optional[str | list] = None,
    host_name: Optional[str | list] = None,
    num_gpus: int = 0,
) -> str:
    """Build the quick start command string"""
    gpu_flag = f" -g {num_gpus}" if num_gpus > 0 else ""
    cluster_flag = ""
    if cluster_name is not None:
        if not isinstance(cluster_name, list):
            cluster_name = [cluster_name]
        cluster_flag = f" -c {' '.join(cluster_name)}"
    host_flag = ""
    if host_name is not None:
        if not isinstance(host_name, list):
            host_name = [host_name]
        host_flag = f" -H {' '.join(host_name)}"
    return f"bl{cluster_flag}{host_flag}{gpu_flag}"




def main():
    try:
        parser = argparse.ArgumentParser(description="Beaker Launch Tool")
        parser.add_argument("-c", "--clusters", nargs="+", help="Cluster names")
        parser.add_argument("-H", "--hosts", nargs="+", help="Host names")
        parser.add_argument("-g", "--gpus", type=int, help="Number of GPUs")
        args = parser.parse_args()

        selector = ClusterSelector(max_width=100)

        if args.clusters or args.hosts:
            # Direct launch with command line arguments
            launch_command = build_launch_command(
                cluster_name=args.clusters,
                host_name=args.hosts,
                num_gpus=args.gpus or 0,
            )
            quick_start_command = build_quick_start_command(
                cluster_name=args.clusters,
                host_name=args.hosts,
                num_gpus=args.gpus or 0,
            )
            
            def on_complete(returncode, output_lines, session_id):
                return handle_session_completion(returncode, output_lines, session_id)
            
            success = curses.wrapper(
                selector.run_direct,
                launch_command,
                quick_start_command,
                args.clusters,
                args.hosts,
                args.gpus or 0,
                on_output_line=None,
                on_complete=on_complete,
            )
            if success and hasattr(selector, "final_output_lines"):
                for line in selector.final_output_lines:
                    print(line)
        else:
            # Interactive menu mode
            def run_interactive(stdscr):
                def on_cluster_selected_internal(stdscr_window, cluster_name, host_name, num_gpus):
                    launch_command = build_launch_command(
                        cluster_name=cluster_name,
                        host_name=host_name,
                        num_gpus=num_gpus,
                    )
                    quick_start_command = build_quick_start_command(
                        cluster_name=cluster_name,
                        host_name=host_name,
                        num_gpus=num_gpus,
                    )
                    
                    def on_complete(returncode, output_lines, session_id):
                        return handle_session_completion(returncode, output_lines, session_id)
                    
                    selector.draw_process_output(
                        stdscr_window,
                        launch_command,
                        quick_start_command,
                        cluster_name,
                        host_name,
                        num_gpus,
                        on_output_line=None,
                        on_complete=on_complete,
                    )
                
                selector.run(stdscr, on_cluster_selected_internal)
            
            curses.wrapper(run_interactive)
            if hasattr(selector, "final_output_lines"):
                for line in selector.final_output_lines:
                    print(line)
    except (KeyboardInterrupt, curses.error):
        sys.exit(0)  # Exit cleanly on Ctrl+C


if __name__ == "__main__":
    main()
