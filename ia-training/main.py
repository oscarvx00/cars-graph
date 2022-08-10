#https://towardsdatascience.com/pca-using-python-scikit-learn-e653f8989e60

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"

#Load dataset
df = pd.read_csv(url, names=['sepal_length', 'sepal width', 'petal length', 'petal width', 'target'])

features = ['sepal_length', 'sepal width', 'petal length', 'petal width']

#Separating out the features
x = df.loc[:, features].values

#Separating out the target
y = df.loc[:,['target']].values

#Standarizing the features
x = StandardScaler().fit_transform(x)

pca = PCA(n_components=2)
principalComponents = pca.fit_transform(x)
principalDf = pd.DataFrame(data = principalComponents, columns=['pc1', 'pc2'])

finalDf = pd.concat([principalDf, df[['target']]], axis=1)

