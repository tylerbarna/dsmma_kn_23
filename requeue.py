import os
import subprocess
import argparse
import shutil
import json

# Function to find and optionally requeue failed jobs
def find_and_requeue_failed_jobs(root_dir, test_run, output_file):
    failed_jobs = {}
    associated_files = {}

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
                    # List associated files (excluding the script itself)
                    associated_files[bash_script] = list_associated_files(dirpath, script_name)
                else:
                    print(f"Requeuing failed job: {bash_script}")
                    # Delete files and subdirectories with the same base filename (excluding the script itself)
                    delete_files_and_subdirs(dirpath, script_name)
                    requeue_failed_job(bash_script)
                failed_jobs[bash_script] = json_file

    if output_file:
        with open(output_file, 'w') as f:
            f.write("\n".join(failed_jobs.keys()))
        
        if test_run:
            associated_file = output_file.replace('.txt', '.json')
            with open(associated_file, 'w') as f:
                json.dump(associated_files, f, indent=2)

# Function to requeue a failed job using sbatch
def requeue_failed_job(script_path):
    try:
        subprocess.run(["sbatch", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to requeue {script_path}: {e}")

# Function to list associated files (excluding the script itself)
def list_associated_files(dirpath, base_filename):
    associated_files = []
    for item in os.listdir(dirpath):
        item_path = os.path.join(dirpath, item)
        if (
            os.path.isfile(item_path)
            or (os.path.isdir(item_path) and item != base_filename)
        ):
            associated_files.append(item_path)
    return associated_files

# Function to delete files and subdirectories with the same base filename (excluding the script itself)
def delete_files_and_subdirs(dirpath, base_filename):
    for item in os.listdir(dirpath):
        item_path = os.path.join(dirpath, item)
        if item != base_filename:
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and requeue failed SLURM jobs.")
    parser.add_argument("--test-run", action="store_true", help="Perform a test run and print script paths and associated files.")
    parser.add_argument("--root-dir", required=True, help="Root directory to search for scripts.")
    parser.add_argument("--output-file", help="File to store the paths of failed jobs.")

    args = parser.parse_args()
    find_and_requeue_failed_jobs(args.root_dir, args.test_run, args.output_file)