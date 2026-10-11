import joblib
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

print("Initializing Multilingual Conceptual Vector Space...")
embedder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# Concept definitions in English. 
# The transformer aligns regional scripts directly to these semantic coordinates.
training_data = [
    ("Garbage dumping, uncollected waste, trash, filth, sewage leakage, dirty streets, sanitation problem", "Sanitation & Garbage"),
    ("Road potholes, broken asphalt, damaged street, traffic hazard, road construction, crater on road", "Roads & Potholes"),
    ("No drinking water supply, pipe leakage, contaminated water, low water pressure, no tap water", "Water Supply"),
    ("Power outage, broken streetlight, electricity failure, transformer sparking, dark street at night", "Electricity"),
    ("Public park maintenance, fallen tree branches, damaged playground, overgrown grass, garden cleanup", "Parks & Recreation")
]

texts = [item[0] for item in training_data]
labels = [item[1] for item in training_data]

# Generate dense vector embeddings
X_embeddings = embedder.encode(texts)

# Train logistic regression on semantic concepts
clf = LogisticRegression()
clf.fit(X_embeddings, labels)

joblib.dump({
    "classifier": clf, 
    "model_name": 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
}, "app/civic_classifier.pkl")

print("Universal multilingual classifier trained and saved to app/civic_classifier.pkl!")