# USE THIS FILE FOR THE FRONTEND STUFF

import tensorflow as tf
from tensorflow import keras
from pathlib import Path
from stringParser3000 import extract_ticker

modelPath = Path(__file__).parent / "sentiment_score_NN.keras"
loadedModel = tf.keras.models.load_model(modelPath)
# replace this variable sentence with a string that is the headline the user wishes to input
sentence = "$TSLA hits an unexpected macro speedbump following delivery numbers, down 4% pre-market."
def predict_financial_insight(raw_sentence):
    score = loadedModel.predict(tf.constant([raw_sentence]), verbose=0)[0][0]
    return {
        "sentence": raw_sentence,
        "extractedTarget": extract_ticker(raw_sentence),
        "predictedSentiment": round(float(score), 4),
    }

def main():
    output = predict_financial_insight(sentence)
    print(output)
if __name__ == "__main__":
    main()