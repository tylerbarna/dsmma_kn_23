import os
import json

def merge_json_files(start_dir, output_file):
    merged_data = []

    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file == 'fit_stats.json':
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    merged_data.append(data)

    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=6)

if __name__ == "__main__":
    start_dir = '/expanse/lustre/projects/umn131/tbarna/ucbeval/Me2017/ucb'
    output_file = 'merged_fit_stats_2.json'
    merge_json_files(start_dir, output_file)
