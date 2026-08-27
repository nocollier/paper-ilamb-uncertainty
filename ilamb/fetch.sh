MODELS=("BCC-ESM1" "CanESM5" "CESM2" "E3SM-1-1" "EC-Earth3-Veg" "GFDL-ESM4" "GISS-E2-1-G" "IPSL-CM6A-LR" "MIROC-ES2L" "MPI-ESM1-2-LR" "UKESM1-0-LL")
mkdir -p _models
for model in "${MODELS[@]}"
do
  echo "Querying ESGF for $model..."
  ilamb esgf study_part.yaml --source-id $model
done
mv *.csv _models
ilamb fetch study.yaml
