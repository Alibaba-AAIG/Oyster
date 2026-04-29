#!/bin/bash
INPUT_PATH="./jailbreak_data/Alibaba_jailbreak_cn_initialization.json"
OUTPUT_DIR="./jailbreak_data"
TOKEN=""
python optimize.py  --token "$TOKEN" --input "$INPUT_PATH"  --output_dir "$OUTPUT_DIR" --start_idx 0