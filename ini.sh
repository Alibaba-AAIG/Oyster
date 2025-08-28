#!/bin/bash
INPUT_PATH="/xxx/xxx/xxx"
TOKEN="xxxxx"
PLATFORM="xxx"
python initialize.py --platform "$PLATFORM" --token "$TOKEN" --input "$INPUT_PATH" --language "en" --stage_inference --stage_safety_chain_extract --stage_safety_chain_recombine --start_idx 0 



