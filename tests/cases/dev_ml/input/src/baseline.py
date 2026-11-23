from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
def run(train, test):
    vec = TfidfVectorizer(ngram_range=(1, 2), max_features=50000)
    clf = LogisticRegression(C=1.0, solver="liblinear", max_iter=1000)
    return f1_score(y_true, y_pred, average="macro")
