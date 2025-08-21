import subprocess
import re
import argparse
from pathlib import Path

USERNAME = 'davidh'

def run_command(cmd, shell=True):
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def update_port(session_id):
    """ Update ~/.ssh/config to point to a session ID """
    # Check if beaker command exists
    stdout, stderr, returncode = run_command("command -v beaker")
    
    if returncode != 0:
        raise RuntimeError(stderr)
    
    # Get beaker session description
    cmd = f"beaker session describe {session_id}" if session_id else "beaker session describe"
    bd_out, stderr, returncode = run_command(cmd)
    
    if not bd_out:
        raise RuntimeError(stderr)

    # Extract hostname
    host_match = re.search(r'([^\s]*\.reviz\.ai2\.in)', bd_out)
    
    if not host_match:
        raise RuntimeError(f"Could not extract hostname: {bd_out}")
    
    host_name = host_match.group(1)

    # Get all port mappings and display them
    print(f"Mapping ports for host: \033[35m{host_name}\033[0m")
    
    # Parse port mappings
    port_mappings = []
    for line in bd_out.split('\n'):
        if '.ai2.in' in line and '->' in line:
            parts = line.split('->')
            if len(parts) >= 2:
                left_part = parts[0].strip()
                right_part = parts[1].strip()
                
                # Extract port from left part (format: host:port)
                if ':' in left_part:
                    remote_port = left_part.split(':')[-1]
                
                # Extract port from right part (format: port/protocol or just port)
                local_port = right_part.split('/')[0]
                
                port_mappings.append((remote_port, local_port))
                print(f"Port: {remote_port} (remote) -> {local_port} (local)")

    # Find specific ports
    server_port = None
    jupyter_port = None
    custom_port0 = None
    custom_port1 = None
    
    for remote_port, local_port in port_mappings:
        if local_port == "8080":
            server_port = remote_port
        elif local_port == "8888":
            jupyter_port = remote_port
        elif local_port == "8000":
            custom_port0 = remote_port
        elif local_port == "8001":
            custom_port1 = remote_port

    # SSH config file path
    config_file = Path.home() / ".ssh" / "config"
    config_file.parent.mkdir(exist_ok=True)
    
    # Read existing config
    config_content = ""
    if config_file.exists():
        config_content = config_file.read_text()

    # Add ai2 host if it doesn't exist
    if "Host ai2" not in config_content:
        ai2_config = "\nHost ai2\n    User root\n    Hostname XXXXX\n    IdentityFile ~/.ssh/id_rsa\n    Port 00000\n"
        config_content += ai2_config
        print(f"Added 'ai2' host to {config_file}")

    # Add ai2-root host if it doesn't exist
    if "Host ai2-root" not in config_content:
        ai2_root_config = f"\nHost ai2-root\n    User {USERNAME}\n    Hostname XXXXX\n    IdentityFile ~/.ssh/id_rsa\n"
        config_content += ai2_root_config
        print(f"Added 'ai2-root' host to {config_file}")

    # Update hostname for both ai2 and ai2-root
    config_lines = config_content.split('\n')
    in_ai2_block = False
    in_ai2_root_block = False
    
    for i, line in enumerate(config_lines):
        if line.strip() == "Host ai2":
            in_ai2_block = True
            in_ai2_root_block = False
        elif line.strip() == "Host ai2-root":
            in_ai2_root_block = True
            in_ai2_block = False
        elif line.strip().startswith("Host ") and line.strip() not in ["Host ai2", "Host ai2-root"]:
            in_ai2_block = False
            in_ai2_root_block = False
        elif (in_ai2_block or in_ai2_root_block) and line.strip().startswith("Hostname"):
            config_lines[i] = f"    Hostname {host_name}"

    # Update port for ai2 host
    in_ai2_block = False
    for i, line in enumerate(config_lines):
        if line.strip() == "Host ai2":
            in_ai2_block = True
        elif line.strip().startswith("Host ") and line.strip() != "Host ai2":
            in_ai2_block = False
        elif in_ai2_block and line.strip().startswith("Port") and server_port:
            config_lines[i] = f"    Port {server_port}"

    # Write updated config
    config_file.write_text('\n'.join(config_lines))

    if server_port:
        print(f"Updated SSH port to \033[35m{host_name}\033[0m:\033[31m{server_port}\033[0m in ~/.ssh/config for ai2 host.")
    else:
        print("No mapping found for remote port 8080 on host ai2. See ~/.ssh/config.")

    # Open SSH tunnel for fast connection
    socket_path = Path.home() / ".ssh" / "ai2locks"
    print(f"Opening SSH tunnel using lock {socket_path}")
    
    socket_path.mkdir(exist_ok=True)
    if socket_path.exists() and not socket_path.is_socket():
        import shutil
        shutil.rmtree(socket_path)
        socket_path.mkdir()

    # Open SSH connection
    run_command("ssh -MNf ai2")

def main():
    parser = argparse.ArgumentParser(description="Update SSH port configuration for Beaker session")
    parser.add_argument("-s", "--session-id", type=str, default="", 
                       help="Beaker session ID to update port for")
    
    args = parser.parse_args()
    
    update_port(args.session_id)
