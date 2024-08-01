#!/bin/bash

# Array of JSON files
json_files=(
    "/root/SWE-bench/final_tasks.json"
)

# Loop through each JSON file
for json_file in "${json_files[@]}"; do
    # Run the python script with the current JSON file
    python3 "/root/SWE-bench/swebench/harness/engine_validation.py" \
        --instances_path "$json_file" \
        --log_dir "/root/data/log_dir_2" \
        --temp_dir "/root/data/temp_dir" \
        --num_workers 100 \
        --timeout 180 \
        --verbose \
        --path_conda "/opt/conda"

    wait
    # Clean up temporary files
    rm -rf /root/data/temp_dir/*
    rm -rf /opt/conda/envs/*_0.0
    cp -r /root/data/log_dir /mnt/llm/home/ibragim-bad/data/swe_log_lite/
    wait
done
