from nltk.translate.meteor_score import meteor_score
from nltk import word_tokenize

# Download required NLTK data (run once)
# import nltk
# nltk.download('wordnet')
# nltk.download('punkt_tab')


reference = "The cat sit mat"
candidate = "cats was sitting rug"

# Tokenize
ref_tokens = word_tokenize(reference.lower())
cand_tokens = word_tokenize(candidate.lower())

# Calculate METEOR
score = meteor_score([ref_tokens], cand_tokens)
print(f"METEOR Score: {score:.4f}")