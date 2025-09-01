#!/bin/bash
INPUT_PATH="./jailbreak_data/Alibaba_jailbreak_cn_initialization.json"
OUTPUT_DIR="./jailbreak_data"
TOKEN="44f5cbe6fc8447ee9de9edcfc3e5db3c"
python optimize.py  --token "$TOKEN" --input "$INPUT_PATH"  --output_dir "$OUTPUT_DIR" --start_idx 0