import tensorflow as tf
import numpy as np
from tensorflow import keras
import argparse
import csv

parser = argparse.ArgumentParser(description='Cars predictor')
parser.add_argument('--source', type=str, required=True, help='csv file path with data source')

args = parser.parse_args()

source_data = []
#Load csv data
with open(args.source) as source_file:
    reader = csv.DictReader(source_file)
    for data in reader:
        source_data.append(data)
    
if len(source_data) == 0:
    print('[ERROR] Source file has no data')  

#Parse integer values
integer_header = ["year", "kms", "seats", "power", "doors", "price"]
for item in source_data:
    for header in integer_header:
        item[header] = int(item[header])


#Load keras model
model = tf.keras.models.load_model('model')

keys = ["brand", "year", "kms", "city", "seats", "power", "transmission", "fuel", "doors", "price"]

predicted_data = []

#Predict for all values, then push to array
for index, car in enumerate(source_data):
    sample = {key: car[key] for key in keys}
    model_dict = {name: tf.convert_to_tensor([value]) for name, value in sample.items()}
    predictions = model.predict(model_dict)
    pred = np.argmax(predictions)
    sample['rating'] = pred
    sample['url'] = source_data[index]['url']
    predicted_data.append(sample)


#Order by rating
predicted_data = sorted(predicted_data, key=lambda d: d['rating'], reverse=True)

#Save predictions to csv
with open('predictions.csv', 'w') as output:
    w = csv.DictWriter(output, predicted_data[0].keys())
    w.writeheader()
    w.writerows(predicted_data)