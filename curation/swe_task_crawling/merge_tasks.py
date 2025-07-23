"""
Script to merge all .jsonl files from a specified folder into a single output file.
"""

import argparse
import json
from pathlib import Path


def merge_jsonl_files(input_folder: str, security_file: str, efficiency_file: str):
    """
    Merge all .jsonl files from input_folder into two separate output files based on classification.
    
    Args:
        input_folder (str): Path to the folder containing .jsonl files.
        security_file (str): Path to the output file for Security tasks.
        efficiency_file (str): Path to the output file for Efficiency tasks.
    """
    input_path = Path(input_folder)

    # Check if input folder exists
    if not input_path.exists():
        print(f"Error: Input folder '{input_folder}' does not exist.")
        return False

    if not input_path.is_dir():
        print(f"Error: '{input_folder}' is not a directory.")
        return False

    # Find all .jsonl files in the input folder
    jsonl_files = list(input_path.glob("*.jsonl"))

    if not jsonl_files:
        print(f"No .jsonl files found in '{input_folder}'")
        return False

    # Merge files into Security and Efficiency outputs
    try:
        with open(security_file, 'w', encoding='utf-8') as sec_outf, \
             open(efficiency_file, 'w', encoding='utf-8') as eff_outf:
            for jsonl_file in sorted(jsonl_files):
                with open(jsonl_file, 'r', encoding='utf-8') as inf:
                    for line in inf:
                        line = line.strip()
                        if line:  # Skip empty lines
                            # Validate JSON format
                            try:
                                task_instance = json.loads(line)
                                classification = task_instance.get("classification", "NA")

                                # Write to the appropriate file based on classification
                                if classification == "Security":
                                    sec_outf.write(line + '\n')
                                elif classification == "Efficiency":
                                    eff_outf.write(line + '\n')
                                # Ignore tasks classified as NA
                            except json.JSONDecodeError as e:
                                print(f"  Warning: Invalid JSON in {jsonl_file.name}: {e}")
                                continue
        return True
    except Exception as e:
        print(f"Error during merge: {e}")
        return False


def main():
    """Main function to handle command line arguments and execute merge."""
    parser = argparse.ArgumentParser(
        description="Merge all .jsonl files from a folder into two output files based on classification",
    )

    parser.add_argument(
        'input_folder',
        nargs='?',
        default='output/tasks',
        help='Folder containing .jsonl files to merge (default: output/tasks)'
    )

    parser.add_argument(
        '--security-output',
        dest='security_file',
        default='output/security_tasks.jsonl',
        help='Output file path for Security tasks (default: output/security_tasks.jsonl)'
    )

    parser.add_argument(
        '--efficiency-output',
        dest='efficiency_file',
        default='output/efficiency_tasks.jsonl',
        help='Output file path for Efficiency tasks (default: output/efficiency_tasks.jsonl)'
    )

    args = parser.parse_args()

    # Execute merge
    success = merge_jsonl_files(args.input_folder, args.security_file, args.efficiency_file)

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
