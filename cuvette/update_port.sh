#!/bin/bash

if ! command -v beaker &> /dev/null; then
    echo "beaker not found"
    exit 1
fi

BD_OUT=$(beaker session describe ${1:+$1})
HOST_NAME=$(echo "$BD_OUT" | grep -o '[^[:space:]]*\.reviz\.ai2\.in' | head -n 1)

if [ -z "$BD_OUT" ]; then
    return 1
fi

# Get all port mappings
autoload -U colors && colors
echo "Mapping ports for host: $fg[magenta]$HOST_NAME$reset_color"
echo "$BD_OUT" | awk -F'->' '/\.ai2\.in/ {
    split($1, a, ":")
    split($2, b, "/")
    print "Port: " a[2] " (remote) -> " b[1] " (local)"
}'

# Get the port which maps to 8080 (openssh)
server_port=$(echo "$BD_OUT" | awk -F'->' '/\.ai2\.in/ {
    split($1, a, ":")
    split($2, b, "/")
    if (b[1] == 8080) {
        print a[2]
    }
}')
jupyter_port=$(echo "$BD_OUT" | awk -F'->' '/\.ai2\.in/ {
    split($1, a, ":")
    split($2, b, "/")
    if (b[1] == 8888) {
        print a[2]
    }
}')
custom_port0=$(echo "$BD_OUT" | awk -F'->' '/\.ai2\.in/ {
    split($1, a, ":")
    split($2, b, "/")
    if (b[1] == 8000) {
        print a[2]
    }
}')
custom_port1=$(echo "$BD_OUT" | awk -F'->' '/\.ai2\.in/ {
    split($1, a, ":")
    split($2, b, "/")
    if (b[1] == 8001) {
        print a[2]
    }
}')

# Add ai2 to ssh config, if it doesn't exist
CONFIG_FILE="$HOME/.ssh/config"
if ! grep -q "Host ai2" "$CONFIG_FILE"; then
    echo -e "\nHost ai2\n    User root\n    Hostname XXXXX\n    IdentityFile ~/.ssh/id_rsa\n    Port 00000" >> "$CONFIG_FILE"
    echo "Added 'ai2' host to $CONFIG_FILE"
fi

# Add ai2 to ssh config, if it doesn't exist
CONFIG_FILE="$HOME/.ssh/config"
if ! grep -q "Host ai2-root" "$CONFIG_FILE"; then
    echo -e "\nHost ai2-root\n    User davidh\n    Hostname XXXXX\n    IdentityFile ~/.ssh/id_rsa" >> "$CONFIG_FILE"
    echo "Added 'ai2-root' host to $CONFIG_FILE"
fi

# Replace hostname for ai2
sed -i '' "/^Host ai2$/,/^$/s/^[[:space:]]*Hostname.*$/    Hostname $HOST_NAME/" ~/.ssh/config
sed -i '' "/^Host ai2-root$/,/^$/s/^[[:space:]]*Hostname.*$/    Hostname $HOST_NAME/" ~/.ssh/config # also replace for root conifg

# Replace the Port line in ~/.ssh/config for Host ai2 with the new local_port
hosts=("ai2")
echo "Updated SSH port to $fg[magenta]$HOST_NAME$reset_color:$fg[red]$server_port$reset_color in ~/.ssh/config for ai2 host."
for host_alias in "${hosts[@]}"; do
    if [ -n "$server_port" ]; then
        sed -i.bak '/^Host '"$host_alias"'$/,/^$/s/^    Port .*/    Port '"$server_port"'/' ~/.ssh/config
    else
        echo "No mapping found for remote port 8080 on host $host_alias. See ~/.ssh/config."
    fi
done

# Open SSH tunnel for fast connection
SOCKET="$HOME/.ssh/ai2locks" # delete any existing locks
echo "Opening SSH tunnel using lock $SOCKET"
mkdir -p "$SOCKET"
if [ -e "$SOCKET" ] && ! [ -S "$SOCKET" ]; then
  rm -rf "$SOCKET"
  mkdir "$SOCKET"
fi
ssh -MNf ai2