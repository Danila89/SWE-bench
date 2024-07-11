import argparse 
import json 
from make_lite import filter_problem_statement, filter_patch, filter_patch_test


def apply_local_filters(dset: list, filters: list[callable]):
    for _filter in filters:
        print(f'Applying {_filter.__name__}.')
        dset = list(filter(_filter, dset))
        print(f'After filtering {len(dset)}.')
    return dset


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, help="Path to json file", required=True)
    parser.add_argument("--output", default="filtered.json", type=str, help="Path to output json file")
    args = parser.parse_args()

    with open(args.file) as f:
        data = json.load(f)

    lite = apply_local_filters(data, [filter_problem_statement, filter_patch, filter_patch_test])

    with open(args.output, 'w') as f:
        json.dump(lite, f, indent=2)
    
    print(f"Saved to {args.output}.")