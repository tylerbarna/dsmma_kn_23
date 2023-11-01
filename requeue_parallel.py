import os
import subprocess
import argparse
import shutil
import json
from collections import defaultdict
from multiprocessing import Pool, Manager

# Function to find and optionally requeue failed jobs for a single directory
def process_directory(directory, test_run, output_file, failed_jobs_list, associated_files_list):
    failed_jobs = {}
    associated_files = {}

    total_jobs = 0
    directory_total_size = 0

    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            directory_total_size += os.path.getsize(os.path.join(dirpath, filename))
            if filename.endswith(".sh"):
                total_jobs += 1
                bash_script = os.path.abspath(os.path.join(dirpath, filename))
                
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

    # Append the failed jobs and associated files to the shared lists
    failed_jobs_list.append(failed_jobs)
    associated_files_list.append(associated_files)
    
    return total_jobs, directory_total_size, len(failed_jobs)

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
        if item.endswith(".sh"):
            continue
        elif base_filename not in item:
            continue
        item_path = os.path.abspath(os.path.join(dirpath, item))
        item_name = os.path.splitext(item)[0]
        if (
            os.path.isfile(item_path)
            or (os.path.isdir(item_path) and item != base_filename)
            and base_filename in item_name
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
    parser.add_argument("--output-file", help="File to store the paths of failed jobs.", default=None)
    parser.add_argument("--stats", action="store_true", help="Print statistics")
    args = parser.parse_args()
    
    ## if output_file string does not contain .txt at the end, add it
    if args.output_file:
        args.output_file = args.output_file if args.output_file.endswith('.txt') else args.output_file + '.txt'
    
    root_dir = args.root_dir

    # Manager to create shared lists for failed jobs and associated files
    with Manager() as manager:
        failed_jobs_list = manager.list()
        associated_files_list = manager.list()

        with Pool() as pool:
            # Process directories in parallel
            results = pool.starmap(process_directory, [(dirpath, args.test_run, args.output_file, failed_jobs_list, associated_files_list) for dirpath, _, _ in os.walk(root_dir)])
            
        total_jobs = 0
        directory_total_size = 0
        num_failed_jobs = 0

        # Accumulate statistics from each process
        for result in results:
            total_jobs += result[0]
            directory_total_size += result[1]
            num_failed_jobs += result[2]

        if args.stats:
            # Print the final statistics
            print(f"\nFinal Statistics:")
            #print(f"Directory size: {directory_total_size / 1e9 :.2f} GB")
            print(f"Total number of jobs: {total_jobs}")
            print(f"Number of failed jobs: {num_failed_jobs}")
            percent_failed = (num_failed_jobs / total_jobs) * 100 if total_jobs > 0 else 0
            print(f"Percentage of jobs that have failed: {percent_failed:.2f}%")
            
        # Combine failed jobs and associated files from each process
        final_failed_jobs = {}
        for jobs in failed_jobs_list:
            final_failed_jobs.update(jobs)

        final_associated_files = {}
        for files in associated_files_list:
            final_associated_files.update(files)

        # if args.stats:
        #     # Print the final statistics
        #     print("\nBreakdown by Model:")
        #     for model, count in failed_jobs_per_model.items():
        #         print(f"Model: {model}, Failed Jobs: {count}, Percentage: {count / total_jobs * 100:.2f}%") if total_jobs > 0 else None

        #     print("\nBreakdown by Lightcurve Type:")
        #     for lightcurve_type, count in failed_jobs_per_lightcurve.items():
        #         print(f"Lightcurve Type: {lightcurve_type}, Failed Jobs: {count}, Percentage: {count / total_jobs * 100:.2f}%") if total_jobs > 0 else None

        #     print("\nHighest Failure Rate Lightcurve Type/Model Fit Combinations:")
        #     sorted_lightcurve_model_failures = sorted(lightcurve_model_failures.items(), key=lambda x: x[1], reverse=True)[:5]
        #     for pairing, count in sorted_lightcurve_model_failures:
        #         lightcurve, model = pairing
        #         percentage = (count / num_failed_jobs) * 100 if num_failed_jobs > 0 else 0
        #         print(f"Lightcurve Type: {lightcurve}, Model: {model}, Failures: {count}, Percentage: {percentage:.2f}%")

        if args.output_file:
            with open(args.output_file, 'w') as f:
                for job in sorted(final_failed_jobs.keys()):
                    f.write(job + '\n')
        
            associated_file = args.output_file.replace('.txt', '.json')
            with open(associated_file, 'w') as f:
                json.dump(final_associated_files, f, indent=2)
