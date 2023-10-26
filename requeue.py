import os
import subprocess
import argparse

# Function to find and optionally requeue failed jobs
def find_and_requeue_failed_jobs(root_dir, test_run, output_file):
    failed_jobs = []

    for dirpath, _, filenames in os.walk(root_dir):
        # Check if a bash script is present in the current directory
        bash_script = None
        for filename in filenames:
            if filename.endswith(".sh"):
                bash_script = os.path.join(dirpath, filename)
                break

        if bash_script is not None:
            # Check if the corresponding JSON file is missing
            script_name = os.path.splitext(os.path.basename(bash_script))[0]
            json_file = os.path.join(dirpath, f"{script_name}_result.json")
            if not os.path.exists(json_file):
                if test_run:
                    print(f"Found failed job: {bash_script}")
                else:
                    print(f"Requeuing failed job: {bash_script}")
                    requeue_failed_job(bash_script)
                failed_jobs.append(bash_script)

    if output_file:
        with open(output_file, 'w') as f:
            f.write("\n".join(failed_jobs))

# Function to requeue a failed job using sbatch
def requeue_failed_job(script_path):
    try:
        subprocess.run(["sbatch", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to requeue {script_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and requeue failed SLURM jobs.")
    parser.add_argument("--test-run", action="store_true", help="Perform a test run and print script paths only.")
    parser.add_argument("--root-dir", required=True, help="Root directory to search for scripts.")
    parser.add_argument("--output-file", help="File to store the paths of failed jobs.")

    args = parser.parse_args()
    find_and_requeue_failed_jobs(args.root_dir, args.test_run, args.output_file)

