
#!/bin/bash
# Number of JSON files to iterate through
num_files=152  # Adjust this number as needed

# Loop through each index to generate the JSON file paths
for i in $(seq 0 $num_files); do
    json_file="/root/data/swe/tasks_${i}.json"
    echo "tasks_${i}.json" >> /root/data/progress.txt

    # Run the python script with the current JSON file
    python3 "/root/SWE-bench/swebench/harness/engine_validation.py" \
        --instances_path "$json_file" \
        --log_dir "/root/data/log_dir_2" \
        --temp_dir "/root/data/temp_dir" \
        --num_workers 100 \
        --timeout 180 \
        --verbose \
        --path_conda "/opt/conda"

    # Clean up temporary files
    rm -rf /root/data/temp_dir/*
    rm -rf /opt/conda/envs/*_0.0
    cp -r /root/data/log_dir_2 /mnt/llm/home/ibragim-bad/data/swe_large_new
    conda clean -a -y
done
