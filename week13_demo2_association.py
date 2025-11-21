from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

career = ["executive", "management", "professional", "salary"]

male = ["Oliver","Michael","Steve"]
female = ["Amy","Mary","Susan"]

career_vecs = model.encode(career, convert_to_numpy=True)
male_vecs = model.encode(male, convert_to_numpy=True)
female_vecs = model.encode(female, convert_to_numpy=True)

scores = []
for word_vec in career_vecs:
    male_sim = cosine_similarity([word_vec], male_vecs).mean()
    female_sim = cosine_similarity([word_vec], female_vecs).mean()
    score = male_sim - female_sim
    scores.append(score)

for c,s in zip(career, scores):
    print(f"{c} -> {s}")

print("Average association:", np.mean(scores))