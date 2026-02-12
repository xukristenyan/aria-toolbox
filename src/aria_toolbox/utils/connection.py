import subprocess


def update_iptables() -> None:
    """
    Update firewall to permit incoming UDP connections for DDS
    """
    update_iptables_cmd = [
        "sudo",
        "iptables",
        "-A",
        "INPUT",
        "-p",
        "udp",
        "-m",
        "udp",
        "--dport",
        "7000:8000",
        "-j",
        "ACCEPT",
    ]
    subprocess.run(update_iptables_cmd)