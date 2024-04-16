from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer
import numpy as np
from scipy.special import softmax

tokenizer = AutoTokenizer.from_pretrained('app/model/', local_files_only=True)
labels = ['anger', 'joy', 'optimism', 'sadness']
model = AutoModelForSequenceClassification.from_pretrained('app/model/', local_files_only=True)

def preprocess(raw): # raw data input for data cleaning
    new_text = []
    for t in raw.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

#  PT
def analysis(textin): # After cleaning and configured with pandas, text is analysis and scored using the function below
    text = preprocess(textin)
    encoded_input = tokenizer(text, return_tensors='pt')
    output = model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)

    # ranking = np.argsort(scores)
    # ranking = ranking[::-1]
    results = []
    for i in range(scores.shape[0]):
        # l = labels[ranking[i]]
        # s = scores[ranking[i]]
        results.append(f"{i+1}) {np.round(float(scores[i]), 4)}")

    return results
