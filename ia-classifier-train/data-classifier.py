"""
Title: Structured data classification from scratch
Author: [fchollet](https://twitter.com/fchollet)
Date created: 2020/06/09
Last modified: 2020/06/09
Description: Binary classification of structured data including numerical and categorical features.
"""
"""
## Introduction
This example demonstrates how to do structured data classification, starting from a raw
CSV file. Our data includes both numerical and categorical features. We will use Keras
preprocessing layers to normalize the numerical features and vectorize the categorical
ones.
Note that this example should be run with TensorFlow 2.5 or higher.
### The dataset
[Our dataset](https://archive.ics.uci.edu/ml/datasets/heart+Disease) is provided by the
Cleveland Clinic Foundation for Heart Disease.
It's a CSV file with 303 rows. Each row contains information about a patient (a
**sample**), and each column describes an attribute of the patient (a **feature**). We
use the features to predict whether a patient has a heart disease (**binary
classification**).
Here's the description of each feature:
Column| Description| Feature Type
------------|--------------------|----------------------
Age | Age in years | Numerical
Sex | (1 = male; 0 = female) | Categorical
CP | Chest pain type (0, 1, 2, 3, 4) | Categorical
Trestbpd | Resting blood pressure (in mm Hg on admission) | Numerical
Chol | Serum cholesterol in mg/dl | Numerical
FBS | fasting blood sugar in 120 mg/dl (1 = true; 0 = false) | Categorical
RestECG | Resting electrocardiogram results (0, 1, 2) | Categorical
Thalach | Maximum heart rate achieved | Numerical
Exang | Exercise induced angina (1 = yes; 0 = no) | Categorical
Oldpeak | ST depression induced by exercise relative to rest | Numerical
Slope | Slope of the peak exercise ST segment | Numerical
CA | Number of major vessels (0-3) colored by fluoroscopy | Both numerical & categorical
Thal | 3 = normal; 6 = fixed defect; 7 = reversible defect | Categorical
Target | Diagnosis of heart disease (1 = true; 0 = false) | Target
"""

"""
## Setup
"""

from cProfile import label
import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow import keras
from keras import layers
from sklearn.preprocessing import LabelBinarizer
from keras.models import Sequential

"""
## Preparing the data
Let's download the data and load it into a Pandas dataframe:
"""

dataframe = pd.read_csv('train_data.csv')
dataframe = dataframe.drop(['url'], axis=1)

"""
The dataset includes 303 samples with 14 columns per sample (13 features, plus the target
label):
"""

dataframe.shape

"""
Here's a preview of a few samples:
"""

dataframe.head()

"""
The last column, "target", indicates whether the patient has a heart disease (1) or not
(0).
Let's split the data into a training and validation set:
"""

val_dataframe = dataframe.sample(frac=0.2, random_state=1337)
train_dataframe = dataframe.drop(val_dataframe.index)

print(
    "Using %d samples for training and %d for validation"
    % (len(train_dataframe), len(val_dataframe))
)

"""
Let's generate `tf.data.Dataset` objects for each dataframe:
"""


def dataframe_to_dataset(dataframe):
    dataframe = dataframe.copy()
    labels = dataframe.pop("rating")
    #label_binarizer = LabelBinarizer()
    #labels_as_binary = label_binarizer.fit_transform(labels)
    #ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels_as_binary))
    ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
    ds = ds.shuffle(buffer_size=len(dataframe))
    return ds


train_ds = dataframe_to_dataset(train_dataframe)
val_ds = dataframe_to_dataset(val_dataframe)

"""
Each `Dataset` yields a tuple `(input, target)` where `input` is a dictionary of features
and `target` is the value `0` or `1`:
"""

for x, y in train_ds.take(1):
    print("Input:", x)
    print("Target:", y)

"""
Let's batch the datasets:
"""

train_ds = train_ds.batch(10)
val_ds = val_ds.batch(10)

"""
## Feature preprocessing with Keras layers
The following features are categorical features encoded as integers:
- `sex`
- `cp`
- `fbs`
- `restecg`
- `exang`
- `ca`
We will encode these features using **one-hot encoding**. We have two options
here:
 - Use `CategoryEncoding()`, which requires knowing the range of input values
 and will error on input outside the range.
 - Use `IntegerLookup()` which will build a lookup table for inputs and reserve
 an output index for unkown input values.
For this example, we want a simple solution that will handle out of range inputs
at inference, so we will use `IntegerLookup()`.
We also have a categorical feature encoded as a string: `thal`. We will create an
index of all possible features and encode output using the `StringLookup()` layer.
Finally, the following feature are continuous numerical features:
- `age`
- `trestbps`
- `chol`
- `thalach`
- `oldpeak`
- `slope`
For each of these features, we will use a `Normalization()` layer to make sure the mean
of each feature is 0 and its standard deviation is 1.
Below, we define 3 utility functions to do the operations:
- `encode_numerical_feature` to apply featurewise normalization to numerical features.
- `encode_string_categorical_feature` to first turn string inputs into integer indices,
then one-hot encode these integer indices.
- `encode_integer_categorical_feature` to one-hot encode integer categorical features.
"""

from keras.layers import IntegerLookup
from keras.layers import Normalization
from keras.layers import StringLookup


def encode_numerical_feature(feature, name, dataset):
    # Create a Normalization layer for our feature
    normalizer = Normalization()

    # Prepare a Dataset that only yields our feature
    feature_ds = dataset.map(lambda x, y: x[name])
    feature_ds = feature_ds.map(lambda x: tf.expand_dims(x, -1))

    # Learn the statistics of the data
    normalizer.adapt(feature_ds)

    # Normalize the input feature
    encoded_feature = normalizer(feature)
    return encoded_feature



def encode_categorical_feature(feature, name, dataset, is_string):
    lookup_class = StringLookup if is_string else IntegerLookup
    # Create a lookup layer which will turn strings into integer indices
    lookup = lookup_class(output_mode="binary")

    # Prepare a Dataset that only yields our feature
    feature_ds = dataset.map(lambda x, y: x[name])
    feature_ds = feature_ds.map(lambda x: tf.expand_dims(x, -1))

    # Learn the set of possible string values and assign them a fixed integer index
    lookup.adapt(feature_ds)

    # Turn the string input into integer indices
    encoded_feature = lookup(feature)
    return encoded_feature


"""
## Build a model
With this done, we can create our end-to-end model:
"""



# Categorical feature encoded as string
brand = keras.Input(shape=(1,), name="brand", dtype="string")
city = keras.Input(shape=(1,), name="city", dtype="string")
transmission = keras.Input(shape=(1,), name="transmission", dtype="string")
fuel = keras.Input(shape=(1,), name="fuel", dtype="string")

# Numerical features
year = keras.Input(shape=(1,), name="year")
kms = keras.Input(shape=(1,), name="kms")
seats = keras.Input(shape=(1,), name="seats")
power = keras.Input(shape=(1,), name="power")
doors = keras.Input(shape=(1,), name="doors")
price = keras.Input(shape=(1,), name="price")

all_inputs = [
    brand,
    city,
    transmission,
    fuel,
    year,
    kms,
    seats,
    power,
    doors,
    price
]

# String categorical features
brand_encoded = encode_categorical_feature(brand, "brand", train_ds, True)
city_encoded = encode_categorical_feature(city, "city", train_ds, True)
transmission_encoded = encode_categorical_feature(transmission, "transmission", train_ds, True)
fuel_encoded = encode_categorical_feature(fuel, "fuel", train_ds, True)

# Numerical features
year_encoded = encode_numerical_feature(year, "year", train_ds)
kms_encoded = encode_numerical_feature(kms, "kms", train_ds)
seats_encoded = encode_numerical_feature(seats, "seats", train_ds)
power_encoded = encode_numerical_feature(power, "power", train_ds)
doors_encoded = encode_numerical_feature(doors, "doors", train_ds)
price_encoded = encode_numerical_feature(price, "price", train_ds)

all_features = [
        brand_encoded,
        city_encoded,
        transmission_encoded,
        fuel_encoded,
        year_encoded,
        kms_encoded,
        seats_encoded,
        power_encoded,
        doors_encoded,
        price_encoded,
    ]

concatenate_layer = layers.Concatenate()
all_features_concatenated = concatenate_layer(all_features)

x = layers.Dense(20, activation="relu")(all_features_concatenated)
hidden = layers.Dense(15, activation='relu')(x)
output = layers.Dense(5, activation="softmax")(hidden)
model = keras.Model(all_inputs, output)

#model = Sequential()
#model.add(all_features_concatenated)
#model.add(layers.Dense(20, activation="relu"))
#model.add(layers.Dense(15, activation='relu'))
#model.add(layers.Dense(5, activation="softmax"))

model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
keras.utils.plot_model(model, show_shapes=True, rankdir="LR")




"""
Let's visualize our connectivity graph:
"""

# `rankdir='LR'` is to make the graph horizontal.


"""
## Train the model
"""

model.fit(train_ds, epochs=50, validation_data=val_ds)
"""
We quickly get to 80% validation accuracy.
"""

"""
## Inference on new data
To get a prediction for a new sample, you can simply call `model.predict()`. There are
just two things you need to do:
1. wrap scalars into a list so as to have a batch dimension (models only process batches
of data, not single samples)
2. Call `convert_to_tensor` on each feature
"""

#Save model
model.save('model')

sample = {
    "brand" : "MERDECES-BENZ",
    "year" : 2002,
    "kms" : 200000,
    "city" : "Alicante",
    "seats" : 4,
    "power" : 218,
    "transmission" : "Autom??tico",
    "fuel" : "Gasolina",
    "doors" : 2,
    "price" : 5000
}

input_dict = {name: tf.convert_to_tensor([value]) for name, value in sample.items()}
predictions = model.predict(input_dict)

pred = np.argmax(predictions)
print("Coche cat " + str(pred))


