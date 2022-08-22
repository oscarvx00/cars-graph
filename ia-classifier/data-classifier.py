from logging.config import valid_ident
from xml.sax.handler import all_features
import tensorflow as tf
import numpy as np
import pandas as pd

import keras
from keras.layers import Normalization
from keras.layers import IntegerLookup
from keras.layers import StringLookup
from keras.layers import Dense
from keras import layers
from keras.utils import plot_model
from keras.models import Sequential

from sklearn.preprocessing import LabelBinarizer

BATCH_SIZE = 10


dataframe = pd.read_csv('train_data.csv')
dataframe = dataframe.drop(['url'], axis=1)


features = dataframe.copy()
labels = dataframe.pop('rating')

inputs = {}

for name, column in features.drop(['rating'], axis=1).items():
    dtype = column.dtype
    if dtype == object:
        dtype = tf.string
    else:
        dtype = tf.float32
    
    inputs[name] = keras.Input(shape=(1,), name=name, dtype=dtype)

print(inputs)


#Procesamiento de entradas numericas concatenadas

numeric_inputs = {
    name: input for name, input in inputs.items() if input.dtype == tf.float32
}
#Capa concat
concatenate_layer = layers.Concatenate()
x = concatenate_layer(list(numeric_inputs.values()))
#Capa normalizacion
norm = layers.Normalization()
norm.adapt(np.array(dataframe[numeric_inputs.keys()]))
#Aplicacion normalizacion
all_numeric_inputs = norm(x)

preprocessed_inputs = [all_numeric_inputs]



#Procesamiento de entradas categoricas
for name, input in inputs.items():

    if input.dtype == tf.float32:
        continue

    #Capa StringLookup mapea a enteros
    lookup = layers.StringLookup()
    lookup.adapt(features[name])

    one_hot = layers.CategoryEncoding(
        num_tokens=lookup.vocabulary_size(),
        output_mode='multi_hot'
    )

    x = lookup(input)
    x = one_hot(x)
    preprocessed_inputs.append(x)


#Preprocesamiento de todas las entradas
concatenate_layer = layers.Concatenate()

preprocessed_inputs_cat = concatenate_layer(preprocessed_inputs)

dataframe_preprocessing = keras.Model(inputs, preprocessed_inputs_cat)

keras.utils.plot_model(
    model=dataframe_preprocessing,
    rankdir="LR",
    dpi=72,
    show_shapes=True,
)

dataframe_features_dict = {
    name: np.array(value) for name, value in features.drop(['rating'], axis=1).items()
}
features_dict = {name: values[:1] for name, values in dataframe_features_dict.items()}
dataframe_preprocessing(features_dict)

def model(preprocessing_head, inputs):

    body = keras.Sequential(
        [
            layers.Dense(15, input_dim=54, activation='relu'),
            layers.Dense(15, activation='relu'),
            layers.Dense(5, activation='softmax')
        ],
    )

    preprocessed_inputs = preprocessing_head(inputs)
    result = body(preprocessed_inputs)

    model = keras.Model(
        inputs,
        result
    )

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

dataframe_model = model(
    dataframe_preprocessing,
    inputs
)

keras.utils.plot_model(
    model=dataframe_model,
    rankdir="LR",
    dpi=72,
    show_shapes=True,
)

label_binarizer = LabelBinarizer()
labels_as_binary = label_binarizer.fit_transform(labels)


history = dataframe_model.fit(
    x=dataframe_features_dict,
    y=labels_as_binary,
    epochs=10
)

sample = preprocessed_inputs

dataframe_model.predict(preprocessed_inputs[0])