import tensorflow as tf
import pandas as pd                                         # data processing, CSV file I/O (e.g. pd.read_csv)
import numpy as np                                          # linear algebra
from tensorflow.keras.models import Sequential              # model type
from tensorflow.keras.layers import Dense, Dropout          # dense layer, dropout layer
from tensorflow.keras.activations import relu, sigmoid      # activation functions
from tensorflow.keras.optimizers import SGD                 # stochastic gradient descent
from tensorflow.keras.losses import binary_crossentropy     # cost function

df = pd.read_csv('dataset\Fraud_Detection_Dataset.csv')

cat_columns = df.select_dtypes(include='object').columns
num_columns = df.select_dtypes(include=np.number).columns

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

X = df.drop(columns=['isFraud', 'isFlaggedFraud'])
y = df['isFraud']
smote = SMOTE()

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(drop='first'), ['type']),
        ('num', StandardScaler(), num_columns[:-2])
    ])

p = Pipeline(steps=[('preprocessor', preprocessor)])

Xp = p.fit_transform(X)
Xp, y = smote.fit_resample(Xp, y)

# Creating Neural Network Model

model_vgg7 = Sequential()
model_vgg7.add(Dense(units=256, activation=relu, input_shape=(Xp.shape[1],)))
model_vgg7.add(Dropout(0.2))
model_vgg7.add(Dense(units=128, activation=relu))
model_vgg7.add(Dropout(0.2))
model_vgg7.add(Dense(units=64, activation=relu))
model_vgg7.add(Dropout(0.2))
model_vgg7.add(Dense(units=32, activation=relu))
model_vgg7.add(Dropout(0.2))
model_vgg7.add(Dense(units=16, activation=relu))
model_vgg7.add(Dropout(0.2))
model_vgg7.add(Dense(units=8, activation=relu))
model_vgg7.add(Dropout(0.2))
model_vgg7.add(Dense(units=4, activation=relu))
model_vgg7.add(Dropout(0.2))
model_vgg7.add(Dense(units=2, activation=relu))
model_vgg7.add(Dropout(0.2))
model_vgg7.add(Dense(units=1, activation=sigmoid))

# optimizer is stochastic gradient descent, which is a good default optimizer, for more info see https://keras.io/api/optimizers/sgd/
model_vgg7.compile(
    optimizer=SGD(),
    loss=binary_crossentropy,
    metrics=['accuracy', 'Precision', 'Recall']
)

model_vgg7.summary()

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(Xp, y, test_size=0.2, random_state=42)

# Training the model
history = model_vgg7.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.2)

# Evaluating the model
model_vgg7.evaluate(X_test, y_test)

# Predicting the test set results
y_pred = model_vgg7.predict(X_test)
y_pred = (y_pred > 0.5)

# save model 
model_vgg7.save('model_vgg7.h5')
