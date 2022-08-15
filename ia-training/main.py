#https://towardsdatascience.com/pca-using-python-scikit-learn-e653f8989e60

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

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
principalDf = pd.DataFrame(data=principalComponents, columns=['pc1', 'pc2'])

finalDf = pd.concat([principalDf, df[['target']]], axis=1)

fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1)
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize = 20)
targets = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
colors = ['r', 'g', 'b']
for target, color in zip(targets,colors):
    indicesToKeep = finalDf['target'] == target
    ax.scatter(finalDf.loc[indicesToKeep, 'pc1']
               , finalDf.loc[indicesToKeep, 'pc2']
               , c = color
               , s = 50)
ax.legend(targets)
ax.grid()
print('vamoss')
plt.savefig('/tmp/figs/fig.png')
plt.show()