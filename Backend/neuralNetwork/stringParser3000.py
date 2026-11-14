# something broke when I started renaming files so I had to move the string parser here

import re

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