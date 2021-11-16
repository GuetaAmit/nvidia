import multiprocessing
import subprocess
import psutil
import time
import argparse
from random import randrange


start_time = time.time()

def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
   
    parser.add_argument("--free-space", action="store", type=int, required=True,
                        dest="free_space", help="X - how many free MB?")

    parser.add_argument("--number-of-files", action="store", type=int, required=True,
                    dest="number_of_files", help="Z - how many file do you want to create")

    parser.add_argument("--size", action="store", type=int, required=True,
                        dest="size", help="Y - which size file to create")
    
    arguments = parser.parse_args()
    
    return arguments


def run(cmd):
    exec_cmd = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    a_stdout, a_stderr = exec_cmd.communicate()
    errcode = exec_cmd.returncode
    return a_stdout, errcode, a_stderr


def run_in_parallel(files, size, mountpoint):
    if files > 0:
        # Don't create file in "/"
        if mountpoint != "/":
            pool_args = [{'cmd': f"dd if=/dev/urandom of={mountpoint}/tmp{randrange(2000)}.txt bs={size}MB count=1"} for _ in range(files)]
            with multiprocessing.Pool(len(pool_args)) as p:
                p.map(mp_worker, pool_args)
    else:
        print(f"nothing to create, probably you wanted to create 0 files?")


def mp_worker(args):
    print (f"running {args['cmd']}")
    res = run(args['cmd'])
    out, code, err = res[0], res[1], res[2]
    if code != 0:
        print(f"[ERROR] - {err}")
    if out:
        print(f"[Success] - {out}")


def run_on_partition(X, Z, Y):
    """Get used disk space."""
    partitions = psutil.disk_partitions(False)
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        if "/loop" in partition.device:
            continue
        # 10 ** 6 - convert between bytes to MB
        free_space_in_MB = usage.free / (10**6)
        # Do you have enough space?
        if free_space_in_MB > X:
            if free_space_in_MB > Z * Y:
                run_in_parallel(Z, Y, partition.mountpoint)
            else:
                print(f"You don't have eonugh space {Y*Z}MB in order to create {Z} file of size {Y}")
        else:
            print(f"You don't have more than {X}MB space in {partition.mountpoint}")


def main():
    arguments = parse_args()
    run_on_partition(arguments.free_space, arguments.number_of_files, arguments.size)
    print(f"----- {time.time() - start_time:.2f} seconds -----" )


if __name__ == "__main__":
    main()