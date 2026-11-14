# DO NOT RUN THIS FILE ON THE FRONTEND UNLESS WE PLAN TO MAKE THE NN BETTER, THIS FILE RETAINS THE NETWORK AND OUTPUTS A FILE EVERY TIME IT IS RUN. WHY AM I YELLING? AAAAAAAAA

import re
import numpy as np
import pandas as pd
import tensorflow as tf
from datasets import load_dataset
from tensorflow.keras.layers import TextVectorization, Embedding, Bidirectional, LSTM, Dense, Dropout, Input
from tensorflow.keras.models import Model
from stringParser3000 import extract_ticker

# rip string parser, you shall be missed

def main():
    # load the dataset yo
    dataset = load_dataset("pauri32/fiqa-2018", split="train")
    df = pd.DataFrame(dataset)

    # establishes parsed target column
    df["parsed_target"] = df["sentence"].apply(extract_ticker)

    # checks accuracy of parsing by comparing to the actual defined target column
    matchingTargets = (df["parsed_target"] == df["target"].str.upper()).sum()
    print(f"accuracy: {matchingTargets / len(df) * 100:.2f}%")

    # prepare the data
    MAXVOCABSIZE = 10000
    MAXSEQUENCELENGTH = 64

    # initialize the text vectorization layer variables
    vectorizer = TextVectorization(
        max_tokens=MAXVOCABSIZE,
        output_sequence_length=MAXSEQUENCELENGTH,
        output_mode="int"
    )

    # fit the vectorizor I totally spelt that wrong but im not changing it
    vectorizer.adapt(df["sentence"].values)

    # gets sentiment for input
    ySentiment = df["sentiment_score"].values.astype(np.float32)

    def build_sentiment_model(vectorizer):

        # input layer of text
        inputs = Input(shape=(), dtype=tf.string)

        # vectorize the text
        x = vectorizer(inputs)

        # run the vectorized text through the embedding layer
        x = Embedding(input_dim=MAXVOCABSIZE, output_dim=128, mask_zero=True)(x)

        # bidirectional layer for context of the entire string
        x = Bidirectional(LSTM(64, return_sequences=False))(x)

        # random dropout
        x = Dropout(0.3)(x)

        # dense layer to promote reasoning
        x = Dense(32, activation="relu")(x)

        # singular output neuron just like my brain after this several hour coding adventure
        outputs = Dense(1, activation="linear", name="sentiment_output")(x)
        return Model(inputs=inputs, outputs=outputs)

    # builds the model
    model = build_sentiment_model(vectorizer)
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    model.summary()

    # translate from pandas dataframe to a tensor because I suck at coding and cannot be bothered to do this more efficiently
    sentences = tf.constant(df["sentence"].astype(str).tolist())
    vectorizer.adapt(sentences)

    # train the neural network
    history = model.fit(sentences, ySentiment, epochs=5, batch_size=30, validation_split=0.2)

    # saves to a file
    model.save("sentiment_score_NN.keras")

# you know what this part does
if __name__ == "__main__":
    main()