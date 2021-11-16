import argparse
from os.path import exists, join
from pathlib import Path
from pssh.clients import ParallelSSHClient


def read_creds():
    token_file = join(str(Path.home()), '.machine/.cred')
    if exists(token_file):
        with open(token_file, 'r') as f:
            token = f.read().strip()
        return token

    print("""
    This script assumes you have set up creds in $HOME/.machine/.cred,
    It seems like you don't have the cred file in your home dir.
    In order to create a private token please follow the instructions below:\n\n
    1. Run "mkdir -p $HOME/.machine && touch $HOME/.machine/.cred"
    2. write "username:password" in the create file, meaning the credential in order to login the servers, for example "admin:admin123!"
    3. Make sure you protect this creds, run "chmod 600 $HOME/.machine/.cred"
    4. Re-run the script
    """)
    return None

def get_user_name():
    creds = read_creds()
    if not creds:
        raise ValueError("There is no cred in $HOME/.machine/.token")
    if ":" in creds:
        return creds
    else:
        raise ValueError("Your cred file is not valid")


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--target-machines', action="store", help="""delimited target branches for cherry pick e.g
        '192.168.10.10,192.168.10.11,192.168.10.12'""", type=lambda s: [item for item in s.split(',')], dest="target_machines")
    
    parser.add_argument("--cmd", action="store", type=str, required=True,
                        dest="cmd", help="cmd to run in the machines")
    
    arguments = parser.parse_args()
    
    return arguments


def run_in_parallel(machines, cmd):
    user, password = get_user_name().split(":")[0], get_user_name().split(":")[1]

    client = ParallelSSHClient(machines, user=user, password=password, num_retries=2, timeout=30)

    output = client.run_command(cmd, stop_on_errors=False)
    for host_output in output:
        try:
            for line in host_output.stdout:
                print(line)
        except TypeError:
            print(f"timeOut from {host_output}")


def main ():
    arguments = parse_args()
    run_in_parallel(arguments.target_machines, arguments.cmd)


if __name__ == "__main__":
    main()