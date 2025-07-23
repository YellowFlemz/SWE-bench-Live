#!/bin/bash

# Exit if any command fails
set -e

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Step 0: Navigate to curation directory
cd curation

# Reset folders before starting
echo "Resetting previous outputs..."
rm -rf job_status output
mkdir -p output

# Step 1: Crawl raw repositories
echo "[1/4] Crawling raw repositories..."
python crawl_repo.py \
  --language Python \
  --min_stars 65000 \
  --max_stars 70000 \
  --tokens_file tokens.txt \
  --output_file output/raw_repos.jsonl

# Step 2: Filter repositories
echo "[2/4] Filtering repositories..."
python filter_repo.py \
  --input_file output/raw_repos.jsonl \
  --output_file output/filtered_repos.jsonl \
  --tokens_file tokens.txt \
  --language Python

# Step 3: Run task generation pipeline
echo "[3/4] Crawling Issue-PR task pairs..."
mkdir -p job_status
./swe_task_crawling/run_get_tasks_pipeline.sh \
  --repos-jsonl output/filtered_repos.jsonl \
  --token-file tokens.txt \
  --cutoff-date 20250501 \
  --path-prs output/prs \
  --path-tasks output/tasks \
  --output-dir output/split_jobs

# Step 4: Merge split jobs
echo "[4/4] Merging all split task files into raw_tasks.jsonl..."
python swe_task_crawling/merge_tasks.py -o output/raw_tasks.jsonl

echo "✅ Done. Final tasks saved to: output/raw_tasks.jsonl"
