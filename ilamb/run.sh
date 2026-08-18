
python ../scripts/expand_config.py study_part.yaml > study.yaml
ilamb run study.yaml --model-db CanESM5.csv
