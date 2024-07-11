from make_lite import filter_problem_statement, filter_patch, filter_patch_test
import argparse 
import json 

## write function that will filter out instances based on filter funcs (get one element) result
def apply_local_filters(dset: list, filters: list[callable]):
    """
    Apply a list of filters to a list of instances

    Args:
        dset: List of instances
        filters: List of filter functions

    Returns:
        List of instances that pass all filters
    """
    for _filter in filters:
        print(f'Applying {_filter.__name__}.')
        dset = list(filter(_filter, dset))
        print(f'After filtering {len(dset)}.')
    return dset


if __name__ == "__main__":
    #get json file as argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, help="Path to json file", required=True)
    parser.add_argument("--output", default="filtered.json", type=str, help="Path to output json file")
    args = parser.parse_args()

    #load json file
    with open(args.file) as f:
        data = json.load(f)

    lite = apply_local_filters(data, [filter_problem_statement, filter_patch, filter_patch_test])

    #save filtered json file
    with open(args.output, 'w') as f:
        json.dump(lite, f, indent=2)
    
    print(f"Saved to {args.output}.")