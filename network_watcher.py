import docker
import time
import os

client = docker.from_env()

def watch_networks():
    # Get the sleep interval from the environment variable, default: 60 seconds
    sleep_interval = int(os.getenv("SLEEP_INTERVAL", "60"))

    while True:
        for container in client.containers.list():
            labels = container.labels

            # Only consider containers explicitly marked for the Network Watcher
            if labels.get("network_watcher") != "true":
                continue

            # Find labels that start with 'network_watcher.' but do not end with '.ip'
            network_labels = {
                k: v for k, v in labels.items()
                if k.startswith("network_watcher.network.") and not k.endswith(".ip")
            }

            for network_label, network_name in network_labels.items():
                ip_label = f"{network_label}.ip"

                if ip_label not in labels:
                    print(f"[WARN] Missing IP address for network {network_name} in container {container.name}.")
                    continue

                ip_address = labels[ip_label]

                try:
                    network = client.networks.get(network_name)
                except docker.errors.NotFound:
                    print(f"[ERROR] Network {network_name} not found.")
                    continue

                # Check if the container is already in the network
                if container.attrs["NetworkSettings"]["Networks"].get(network_name):
                    print(f"[INFO] Container {container.name} is already in the network {network_name}.")
                    continue

                # Add the container to the network
                try:
                    network.connect(container, ipv4_address=ip_address)
                    print(f"[SUCCESS] Container {container.name} added to {network_name} with IP {ip_address}.")
                except Exception as e:
                    print(f"[ERROR] Error adding {container.name} to {network_name}: {e}")

        print(f"[INFO] Waiting {sleep_interval} seconds before the next check.")
        time.sleep(sleep_interval)

if __name__ == "__main__":
    watch_networks()
