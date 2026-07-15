# Evaluation/sample_generator.py

import json
import random

with open(
    "../Dataset/english_katakana_output.json",
    encoding="utf-8"
) as f:
    data = json.load(f)

sample = random.sample(
    data,
    min(100, len(data))
)

with open(
    "sample_100.json2",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        sample,
        f,
        ensure_ascii=False,
        indent=4
    )

print("Generated 100-name sample.")