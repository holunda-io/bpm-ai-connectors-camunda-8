import subprocess
import os
import time
import sys


def main():
    # Get the list of processes from command line arguments
    processes_params = [arg.split() for arg in sys.argv[1:]]
    # Start all processes
    processes = [subprocess.Popen(params) for params in processes_params]
    print(f"[init] Started {len(processes)} processes.")
    # Continuously monitor the processes
    while True:
        for i, process in enumerate(processes):
            exit_status = process.poll()
            if exit_status is not None:
                print(f"[init] Process '{' '.join(processes_params[i])}' exited with status {exit_status}, terminating other processes...")
                # Terminate all other processes
                for j, other_process in enumerate(processes):
                    if i != j:
                        other_process.terminate()
                return
        # Sleep for a bit to avoid busy-waiting
        time.sleep(1)


if __name__ == "__main__":
    main()
