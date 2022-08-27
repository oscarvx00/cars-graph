import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow import keras
import argparse
import csv

parser = argparse.ArgumentParser(description='Cars predictor')
parser.add_argument('--source', type=str, required=True, help='csv file path with data source')

args = parser.parse_args()

source_data = pd.read_csv(args.source)

#Load keras model
model = tf.keras.models.load_model('model')

keys = ["brand", "year", "kms", "city", "seats", "power", "transmission", "fuel", "doors", "price"]
source_filtered = source_data.copy()
for col in source_filtered:
    if col not in keys:
        source_filtered = source_filtered.drop(col, axis=1)

#print(source_filtered.head(36))
#Fill with most common
for column in source_filtered:
    most_common = source_filtered[column].mode().values[0]
    source_filtered[column].fillna(most_common, inplace=True)

#print(source_filtered.head(36))

predicted_data = []

#Predict for all values, then push to array
for index, car in source_filtered.iterrows():
    sample = {key: car[key] for key in keys}
    model_dict = {name: tf.convert_to_tensor([value]) for name, value in sample.items()}
    predictions = model.predict(model_dict)
    pred = np.argmax(predictions)
    sample['rating'] = pred
    sample['url'] = source_data.iloc[index]['url']
    predicted_data.append(sample)


#Order by rating
predicted_data = sorted(predicted_data, key=lambda d: d['rating'], reverse=True)

keys.append('rating')
keys.append('url')
#Save predictions to csv
with open('predictions.csv', 'w') as output:
    w = csv.DictWriter(output, keys)
    w.writeheader()
    w.writerows(predicted_data)