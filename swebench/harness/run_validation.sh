
#!/bin/bash
# Number of JSON files to iterate through
num_files=42  # Adjust this number as needed


nums_list=($(seq 0 $num_files))
# Loop through each index to generate the JSON file paths
for i in "${nums_list[@]}"; do
    json_file="/root/data/swe/same_${i}.json"
    echo "tasks_${i}.json" >> /root/data/progress_3.txt

    # # Run the python script with the current JSON file
    python3 "/root/SWE-bench/swebench/harness/engine_validation.py" \
        --instances_path "$json_file" \
        --log_dir "/root/data/log_dir_3" \
        --temp_dir "/root/data/temp_dir" \
        --num_workers 100 \
        --timeout 180 \
        --verbose \
        --path_conda "/opt/conda"

    # # Clean up temporary files
    rm -rf /root/data/temp_dir/*
    rm -rf /opt/conda/envs/*_0.0
    # ##cp in background
    # # cp -r /root/data/log_dir_2 /mnt/llm/home/ibragim-bad/data/swe_large_new &
    # conda clean -a -y
done
