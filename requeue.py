import os
import subprocess
import argparse
import shutil
import json
from collections import defaultdict

# Function to find and optionally requeue failed jobs
def find_and_requeue_failed_jobs(root_dir, test_run, output_file, print_stats):
    failed_jobs = {}
    associated_files = {}

    total_jobs = 0
    failed_jobs_per_model = defaultdict(int)
    failed_jobs_per_lightcurve = defaultdict(int)
    lightcurve_model_failures = defaultdict(int)

    for dirpath, _, filenames in os.walk(root_dir):
        # Check if a bash script is present in the current directory
        bash_script = None
        for filename in filenames:
            if filename.endswith(".sh"):
                total_jobs += 1
                bash_script = os.path.abspath(os.path.join(dirpath, filename))
                break

        if bash_script is not None:
            # Check if the corresponding JSON file is missing
            script_name = os.path.splitext(os.path.basename(bash_script))[0]
            json_file = os.path.abspath(os.path.join(dirpath, f"{script_name}_result.json"))
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

                # Extract lightcurve type and model from the script label
                script_parts = script_name.split("_fit_")
                if len(script_parts) == 2:
                    lightcurve_type, model = script_parts[0], script_parts[1]
                    model = model.split("_")[0]
                    true_lightcurve = lightcurve_type.split("_")[1] if lightcurve_type.startswith("lc_") else lightcurve_type
                    failed_jobs_per_model[model] += 1
                    failed_jobs_per_lightcurve[true_lightcurve] += 1
                    lightcurve_model_failures[(true_lightcurve, model)] += 1

    num_failed_jobs = len(failed_jobs)
    percent_failed = (num_failed_jobs / total_jobs) * 100 if total_jobs > 0 else 0
    num_associated_files = sum(len(files) for files in associated_files.values())

    if print_stats:
        print(f"\nStatistics:")
        print(f"Total number of jobs: {total_jobs}")
        print(f"Number of failed jobs: {num_failed_jobs}")
        print(f"Percentage of jobs that have failed: {percent_failed:.2f}%")
        print(f"Number of files associated with failed jobs: {num_associated_files}")
        print(f"Average number of files associated with each failed job: {num_associated_files / num_failed_jobs:.2f}")

        print("\nBreakdown by Model:")
        for model, count in failed_jobs_per_model.items():
            print(f"Model: {model}, Failed Jobs: {count}, Percentage: {count / total_jobs * 100:.2f}%")

        print("\nBreakdown by Lightcurve Type:")
        for lightcurve_type, count in failed_jobs_per_lightcurve.items():
            print(f"Lightcurve Type: {lightcurve_type}, Failed Jobs: {count}, Percentage: {count / total_jobs * 100:.2f}%")

        # Print the top 5 lightcurve type/model fit pairings with their failure percentages
        print("\nTop 5 Lightcurve Type/Model Fit Pairings:")
        sorted_lightcurve_model_failures = sorted(lightcurve_model_failures.items(), key=lambda x: x[1], reverse=True)[:5]
        for pairing, count in sorted_lightcurve_model_failures:
            lightcurve, model = pairing
            percentage = (count / num_failed_jobs) * 100 if num_failed_jobs > 0 else 0
            print(f"Lightcurve Type: {lightcurve}, Model: {model}, Failures: {count}, Percentage: {percentage:.2f}%")

    if output_file:
        with open(output_file, 'w') as f:
            for job in sorted(failed_jobs.keys()):
                f.write(job + '\n')
        
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
        item_path = os.path.abspath(os.path.join(dirpath, item))
        if (
            os.path.isfile(item_path)
            or (os.path.isdir(item_path) and item != base_filename)
        ):
            associated_files.append(item_path)
    return associated_files

# Function to delete files and subdirectories with the same base filename (excluding the script itself)
def delete_files_and_subdirs(dirpath, base_filename):
    for item in os.listdir(dirpath):
        item_path = os.path.abspath(os.path.join(dirpath, item))
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
    parser.add_argument("--stats", action="store_true", help="Print statistics")
    args = parser.parse_args()
    
    ## if output_file string does not contain .txt at the end, add it
    args.output_file = args.output_file if args.output_file.endswith('.txt') else args.output_file + '.txt'

    find_and_requeue_failed_jobs(args.root_dir, args.test_run, args.output_file, args.stats)