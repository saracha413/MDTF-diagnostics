#!/usr/bin/env python


#############################################################
# Converted version of S Leroy submit_aws_batch.py
# Converted with Copilot by S Vannah
#############################################################

import argparse
import subprocess 
from pyllj.libcli import build_subparsers, process
import os
import re
import sys

from dask_jobqueue import SLURMCluster
from dask.distributed import Client, as_complete


valid_partitions = ["short", "medium", "long"]

class Command:
    def __init__(self, partition: str, runtime: float):
        if partition not in valid_partitions:
            print(
                f'Partition "{partition}" is not valid; must be one of '
                + ", ".join([f'"{p}"' for p in valid_partitions])
            )
            exit()

        self.partition = partition
        self.runtime = float(runtime)

        # Convert runtime hours → Slurm walltime string
        days = int(self.runtime / 24)
        hours = int(self.runtime) % 24
        minutes = int(self.runtime * 60) % 60
        self.walltime = f"{days}-{hours:02d}:{minutes:02d}:00"

        # Create Dask cluster
        self.cluster = SLURMCluster(
            queue=self.partition,
            cores=1,
            memory="1800MB",
            walltime=self.walltime,
            job_extra=["--nodes=1", "--ntasks=1", "--cpus-per-task=1"],
        )
        self.client = Client(self.cluster)

        # Logging directory
        self.logsdir = "logs"
        os.makedirs(self.logsdir, exist_ok=True)

    def __call__(
        self,
        job,
        jobName,
        execute: bool = False,
        dataroot: {str, None} = None,
        memory: int = 1800,
        **kwargs,
    ):
        """
        Submit a single job to Dask instead of SLURM.
        job: list of command-line tokens (originally used to build a shell command)
        jobName: name of the job
        """

        # Remove cdsapi key
        for flag in ["-k", "--key"]:
            if flag in job:
                i = job.index(flag)
                job.pop(i)
                job.pop(i)

      # Remove Earthdata auth
        for flag in ["-a", "--auth"]:
            if flag in job:
                i = job.index(flag)
                job.pop(i)
                job.pop(i)

        # Add dataroot if needed
        if dataroot is not None and "-d" not in job and "--dataroot" not in job:
            job += ["--dataroot", dataroot]

        # Convert job list → command string
        command_str = " ".join(job)

        # Define the function that will run on Dask workers
        def run_job(cmd, jobName):
            import subprocess
            import datetime

            # Activate conda environment
            activate = 'eval "$(conda shell.bash hook)" && conda activate low-level-jet'


            # Log start
            start_msg = f"Job {jobName} starting at {datetime.datetime.now()}"
            print(start_msg)

            # Run command
            full_cmd = f"{activate} && {cmd}"
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)

            # Write logs
            outpath = os.path.join("logs", f"{jobName}.out")
            errpath = os.path.join("logs", f"{jobName}.err")

            with open(outpath, "w") as f:
                f.write(result.stdout)

            with open(errpath, "w") as f:
                f.write(result.stderr)


            # Log end
            end_msg = f"Job {jobName} ending at {datetime.datetime.now()}"
            print(end_msg)

            return result.returncode

        if execute:
            print(f"Submitting job {jobName} to Dask")
            future = self.client.submit(run_job, command_str, jobName)
            return future

        else:
            print(f"Dry run: {jobName}")
            print("Command:", command_str)
            return None

def main():
    parser = argparse.ArgumentParser(
        description="""
        Submit LLJ diagnostic jobs using Dask instead of SLURM.
        """
    )

    default_partition = "short"
    parser.add_argument(
        "--partition",
        "-p",
        dest="partition",
        default=default_partition,
        help="Partition name (short, medium, long).",
    )

   default_runtime = 6.0
    parser.add_argument(
        "--runtime",
        "-r",
        dest="runtime",
        default=default_runtime,
        help=f"Expected runtime in hours (default {default_runtime}).",
    )

    parser = build_subparsers(parser)

    args = parser.parse_args()
    command = Command(args.partition, args.runtime)

    futures = process(args, command)

    # If jobs were submitted, gather results
    if futures:
        results = command.client.gather(futures)
        print("All jobs completed.")
        print(results)


if __name__ == "__main__":
    main()
