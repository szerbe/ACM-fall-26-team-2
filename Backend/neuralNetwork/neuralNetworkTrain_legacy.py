# DO NOT RUN THIS FILE ON THE FRONTEND UNLESS WE PLAN TO MAKE THE NN BETTER, THIS FILE RETAINS THE NETWORK AND OUTPUTS A FILE EVERY TIME IT IS RUN. WHY AM I YELLING? AAAAAAAAA

import re
import numpy as np
import pandas as pd
import tensorflow as tf
from datasets import load_dataset
from tensorflow.keras.layers import TextVectorization, Embedding, Bidirectional, LSTM, Dense, Dropout, Input
from tensorflow.keras.models import Model

# parse the string for stock tickers
def extract_ticker(sentence):
    # scan for a cashtag (like $AAPL)
    cashtags = re.findall(r"\$([A-Z]{1,5})\b", sentence.upper())
    if cashtags:
        return cashtags[0]   
    # just in case theres no cashtags search for patterns of uppercase letters
    words = re.findall(r"\b([A-Z]{2,5})\b", sentence)
    if words:
        return words[0]
    return "unknown ticker"

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

    # gets numbers for input
    xText = vectorizer(df["sentence"].values)
    ySentiment = df["sentiment_score"].values.astype(np.float32)

    # build the actual NN
    def build_sentiment_model():
        # input layer
        inputs = Input(shape=(MAXSEQUENCELENGTH,), dtype=tf.int64)

        # embedding layer
        x = Embedding(input_dim=MAXVOCABSIZE, output_dim=128, mask_zero=True)(inputs)
        
        # bidirectional LSTM so that more context can be gainainededs (I am losing my mind)
        x = Bidirectional(LSTM(64, return_sequences=False))(x)
        x = Dropout(0.3)(x)
        
        # dense layers for that extra reasoning sauce
        x = Dense(32, activation="relu")(x)
        
        # output layer of sentiment score from -1 to 1
        outputs = Dense(1, activation="linear", name="sentiment_output")(x)
        
        model = Model(inputs=inputs, outputs=outputs)
        return model

    model = build_sentiment_model()
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    model.summary()

    # train the neural network
    history = model.fit(xText, ySentiment, epochs=5, batch_size=30, validation_split=0.2)

    # ticker and sentiment variables
    def predict_financial_insight(raw_sentence):
        parsed_ticker = extract_ticker(raw_sentence)
        tokenized_input = vectorizer([raw_sentence])
        predictedSentiment = model.predict(tokenized_input, verbose=0)[0][0]
        return {
            "sentence": raw_sentence,
            "extractedTarget": parsed_ticker,
            "predictedSentiment": round(float(predictedSentiment), 4)
        }

    # input
    # test string: "$TSLA hits an unexpected macro speedbump following delivery numbers, down 4% pre-market."
    def input(inputText):
        insight = predict_financial_insight(inputText)
        print(insight)

    input("Nvidia CEO Huang resigns, effective immediately; CFO Kress takes over")
    model.save("sentiment_score_NN.keras")
main()