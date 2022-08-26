from cProfile import label
import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow import keras

model = tf.keras.models.load_model('model')


sample = {
    "brand" : "MERDECES-BENZ",
    "year" : 2002,
    "kms" : 200000,
    "city" : "Alicante",
    "seats" : 4,
    "power" : 218,
    "transmission" : "Automático",
    "fuel" : "Gasolina",
    "doors" : 2,
    "price" : 5000
}

input_dict = {name: tf.convert_to_tensor([value]) for name, value in sample.items()}
predictions = model.predict(input_dict)

pred = np.argmax(predictions)
print("Coche cat " + str(pred))