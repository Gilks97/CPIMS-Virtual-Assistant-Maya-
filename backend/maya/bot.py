#importing ml libraries
import tensorflow as tf
import numpy as np
import pandas as pd
import json
import nltk
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.layers import Input, Embedding, LSTM , Dense,GlobalMaxPooling1D,Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import matplotlib.pyplot as plt
import string
from sklearn.preprocessing import LabelEncoder
import random


#importing the dataset
with open('test.json') as content:
  data1 = json.load(content)
#getting all the data to lists
tags = []
inputs = []
responses={}
for intent in data1['intents']:
  responses[intent['tag']]=intent['responses']
  for lines in intent['input']:
    inputs.append(lines)
    tags.append(intent['tag'])
#converting to dataframe
data = pd.DataFrame({"inputs":inputs,
                     "tags":tags})
#removing punctuations
data['inputs'] = data['inputs'].apply(lambda wrd:[ltrs.lower() for ltrs in wrd if ltrs not in string.punctuation])
data['inputs'] = data['inputs'].apply(lambda wrd: ''.join(wrd))


#tokenize the data
tokenizer = Tokenizer(num_words=2000)
tokenizer.fit_on_texts(data['inputs'])
train = tokenizer.texts_to_sequences(data['inputs'])

#apply padding
x_train = pad_sequences(train)

#encoding the outputs
le = LabelEncoder()
y_train = le.fit_transform(data['tags'])

#input length
input_shape = x_train.shape[1]
print(input_shape)
#define vocabulary
vocabulary = len(tokenizer.word_index)
print("number of unique words : ",vocabulary)
#output length
output_length = le.classes_.shape[0]
print("output length: ",output_length)


#creating the model
i = Input(shape=(input_shape,))
x = Embedding(vocabulary+1,10)(i)
x = LSTM(10,return_sequences=True)(x)
x = Flatten()(x)
x = Dense(output_length,activation="softmax")(x)
model  = Model(i,x)
#compiling the model
model.compile(loss="sparse_categorical_crossentropy",optimizer='adam',metrics=['accuracy'])
#training the model
train = model.fit(x_train,y_train,epochs=500)


def getBotResponse(data_input):
    #chatting
    while True:
        if data_input == "goodbye":
            return('Thank you. Have a lovely day.')

        texts_p = []
        # prediction_input = input('You : ')
        prediction_input = data_input
        #removing punctuation and converting to lowercase
        prediction_input = [letters.lower() for letters in prediction_input if letters not in string.punctuation]
        prediction_input = ''.join(prediction_input)
        texts_p.append(prediction_input)
        #tokenizing and padding
        prediction_input = tokenizer.texts_to_sequences(texts_p)
        prediction_input = np.array(prediction_input).reshape(-1)
        prediction_input = pad_sequences([prediction_input],input_shape)
        #getting output from model
        output = model.predict(prediction_input)
        output = output.argmax()
        #finding the right tag and predicting
        response_tag = le.inverse_transform([output])[0]
        
        return random.choice(responses[response_tag])