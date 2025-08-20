#!/bin/bash

# Exit if any command fails
set -e

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Step 0: Navigate to launch directory
cd launch

# Step 1: Run test launch
python -m launch.run --config-path test-config.json

# Step 2: Export successfully set up instances to pre-validated SWE-bench-Live instances file
python to_swebench.py --playground playground/test --output_jsonl ../curation/output/pre-validated-instances.jsonl

# THIS IS WHERE INFERENCE HAPPENS NORMALLY, FOR THIS TEST SCRIPT WE USE GOLD PATCHES

# Step 3: Apply gold patches to instances, run test cases and get FAIL_TO_PASS and PASS_TO_PASS test cases for each instance
cd ..
python -m swebench.harness.run_validation --dataset_name curation/output/pre-validated-instances.jsonl \
    --predictions_path gold --max_workers 10 --run_id tutorial-validation --namespace starryzhang

# Step 4: Writes valid instance with both FAIL_TO_PASS and PASS_TO_PASS test cases to final dataset
python swebench/collect/produce/make_full.py --input-dir logs/run_evaluation/tutorial-validation/gold --output-dir datasets

# -------------- NOTE: FINAL STEP MUST BE RUN MANUALLY --------------
# Step 5: Check whether all instances can be solved by the gold patches (usually they do)
# python -m swebench.harness.run_evaluation \
#   --dataset_name datasets/full-{dataset_date}.jsonl \
#   --split full \
#   --predictions_path gold \
#   --run_id tutorial-validation \
#   --rewrite_reports true