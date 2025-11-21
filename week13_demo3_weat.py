from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# Target word sets (the concepts we want to compare)
# Career vs. Family
career = ["executive", "management", "professional", "salary"]
family = ["home", "parents", "children", "family", "school"]

# Attribute word sets (the polar attribute concepts)
# Male vs. Female
male = ["Oliver", "Michael", "Steve"]
female = ["Amy", "Mary", "Susan"]

career_vecs = model.encode(career, convert_to_numpy=True)
family_vecs = model.encode(family, convert_to_numpy=True)
male_vecs = model.encode(male, convert_to_numpy=True)
female_vecs = model.encode(female, convert_to_numpy=True)

# Association (t, A, B) = mean cosine (t, A) - mean cosine (t, B)
# Positive => the word is nearer to A
# Negative => the word is nearer to B
def association(word_vec, A_vecs, B_vecs):
    sim_A = cosine_similarity([word_vec], A_vecs).mean()
    sim_B = cosine_similarity([word_vec], B_vecs).mean()
    return sim_A - sim_B

career_scores = [association(v, male_vecs, female_vecs) for v in career_vecs]
family_scores = [association(v, male_vecs, female_vecs) for v in family_vecs]

# WEAT effect size
mean_career = np.mean(career_scores)
mean_family = np.mean(family_scores)

# sample standard deviation
pooled_std = np.std(career_scores + family_scores, ddof=1)
effect_size = (mean_career - mean_family) / pooled_std

print("WEAT effect size", round(effect_size, 4))