import argparse, os
import random

from multiprocessing import Pool, cpu_count
from swebench.harness.constants import PatchType
from swebench.harness.context_manager import TaskEnvContextManager, TestbedContextManager
from swebench.harness.utils import get_instances, split_instances, DotDict


SKIP_INSTANCES = {"pytest-dev/pytest": ["6387", "7956", "3805"]}


def validate_args(args):
    """
    Validation for command line arguments
    """
    if not os.path.exists(args.instances_path):
        raise ValueError(f"Could not find instances file at {args.instances_path}")
    if not os.path.exists(args.log_dir):
        raise ValueError(f"Could not find log directory at {args.log_dir}")

    # If value is provided, check that the paths exist
    if args.path_conda is not None and not os.path.exists(args.path_conda):
        raise ValueError(f"Could not find conda installation at {args.path_conda}")
    if args.testbed is not None and not os.path.exists(args.testbed):
        raise ValueError(f"Could not find testbed at {args.testbed}")
    if args.temp_dir is not None and not os.path.exists(args.temp_dir):
        raise ValueError(f"Could not find temporary directory at {args.temp_dir}")

    # If value is provided, check that it is valid
    if args.timeout is not None and args.timeout < 0:
        raise ValueError(f"Timeout must be a positive integer")
    if args.num_workers is not None and args.num_workers < 1:
        raise ValueError(f"Number of workers must be a positive integer")


def verify_task_instances(data: dict):
    """
    Sets up task environment context manager. Each task instance is then
    installed and validated within the context manager.

    Args:
        data: Dict containing task instances and other data
            task_instances: List of task instances
            + setup_testbed args
    """
    data_dict = DotDict(data)
    for task_instance in data_dict.task_instances:
        with TaskEnvContextManager(
            task_instance,
            data_dict.testbed,
            data_dict.venv,
            data_dict.log_dir,
            data_dict.conda_path,
            verbose=data_dict.verbose,
            timeout=data_dict.timeout,
            log_suffix=data_dict.log_suffix,
        ) as tcm:
            if (
                task_instance["repo"] in SKIP_INSTANCES
                and task_instance["pull_number"]
                in SKIP_INSTANCES[task_instance["repo"]]
            ):
                continue
            if (
                not tcm.reset_task_env(task_instance)
                or not tcm.run_install_task(task_instance)
                or not tcm.apply_patch(task_instance["test_patch"], patch_type=PatchType.PATCH_TEST.value)
                or not tcm.run_tests_task(task_instance)
                or not tcm.apply_patch(task_instance["patch"], patch_type=PatchType.PATCH_GOLD.value)
                or not tcm.run_tests_task(task_instance)
            ):
                continue


from concurrent.futures import ProcessPoolExecutor
import random
from multiprocessing import cpu_count

def enter_tcm(tcm):
    return tcm.__enter__()

def exit_tcm(tcm):
    tcm.__exit__(None, None, None)

def execute_func(args):
    task_list, func = args
    func(task_list)

def setup_testbed(data: dict, workers: int):
    data_dict = DotDict(data)
    
    # Create TestbedContextManager instances without entering them
    tcm_instances = [
        TestbedContextManager(
            [task_instance],  # Each manager handles one task instance
            data_dict.log_dir,
            conda_link=data_dict.conda_link,
            path_conda=data_dict.path_conda,
            testbed=data_dict.testbed,
            temp_dir=data_dict.temp_dir,
            timeout=data_dict.timeout,
            verbose=data_dict.verbose,
        )
        for task_instance in data_dict.task_instances
    ]
    
    # Parallelize the __enter__ method
    with ProcessPoolExecutor(max_workers=workers) as executor:
        tcm_list = list(executor.map(enter_tcm, tcm_instances))
    
    try:
        distributed_task_list = [tcm.get_distributed_tasks() for tcm in tcm_list]
        flattened_task_list = [item for sublist in distributed_task_list for item in sublist]
        
        for task_list in flattened_task_list:
            print(f"{task_list['testbed']}: {len(task_list['task_instances'])} instances")
        
        # Parallelize data_dict.func execution
        with ProcessPoolExecutor(max_workers=workers) as executor:
            executor.map(execute_func, [(task_list, data_dict.func) for task_list in flattened_task_list])
    
    finally:
        # Ensure proper cleanup
        with ProcessPoolExecutor(max_workers=workers) as executor:
            executor.map(exit_tcm, tcm_list)

def main(args):
    random.seed(42)
    if args.num_workers is None:
        args.num_workers = cpu_count()

    task_instances = get_instances(args.instances_path)
    task_instances = sorted(task_instances, key=lambda x: x["instance_id"])
    if args.instance_id is not None:
        task_instances = [t for t in task_instances if t["instance_id"] in args.instance_id.split(',')]
    if args.sample is not None:
        if len(task_instances) > args.sample:
            task_instances = random.sample(task_instances, args.sample)
    for t in task_instances:
        if "version" not in t:
            t["version"] = "0.0"
    task_instances = sorted(task_instances, key=lambda x: x["instance_id"])

    data = {
        "task_instances": task_instances,
        "func": verify_task_instances,
        **vars(args),
    }
    del data["instances_path"]

    setup_testbed(data, args.num_workers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--instances_path", type=str, help="Path to candidate task instances file", required=True)
    parser.add_argument("--log_dir", type=str, help="Path to log directory", required=True)
    parser.add_argument("--conda_link", type=str, default=None, help="(Optional) URL to conda installation to use")
    parser.add_argument("--log_suffix", type=str, default=None, help="(Optional) Suffix to append to log file names")
    parser.add_argument("--path_conda", type=str, help="(Optional) Path to miniconda3 or anaconda installation")
    parser.add_argument("--testbed", type=str, help="(Optional) Path to testbed directory")
    parser.add_argument("--temp_dir", type=str, help="(Optional) Path to temporary directory for storing virtual envs")
    parser.add_argument("--timeout", type=int, default=None, help="(Optional) Timeout (seconds) for testing script execution")
    parser.add_argument("--verbose", action="store_true", help="(Optional) Verbose mode")
    parser.add_argument("--num_workers", type=int, default=None, help="(Optional) Number of workers")
    parser.add_argument("--instance_id", type=str, default=None, help="(Optional) Instance ID to run")
    parser.add_argument("--sample", type=int, default=None, help="(Optional) Random samples num for validation")
    args = parser.parse_args()
    validate_args(args)
    main(args)
