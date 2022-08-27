cd data-getters/coches-net-py
#python3 main.py --pages 1 --output rawData.csv

cd ../..
mv data-getters/coches-net-py/rawData.csv ia-classifier
docker run --mount type=bind,source="$(pwd)"/ia-classifier,target=/train oscarvicente/cars-graph-train python3 data-classifier.py --source rawData.csv
#rm ia-classifier/rawData.csv