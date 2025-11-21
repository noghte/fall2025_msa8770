from nltk.translate.bleu_score import sentence_bleu
from nltk import word_tokenize

# Download required NLTK data (run once)
# import nltk
# nltk.download('wordnet')
# nltk.download('punkt_tab')


reference = "The cat sat on the mat"
# candidate = "A feline was sitting on the rug"
candidate = "The sat cat on the mat"

ref_tokens = word_tokenize(reference.lower())
cand_tokens = word_tokenize(candidate.lower())

# only include unigrams and bigrams 
bleu = sentence_bleu([ref_tokens], cand_tokens, weights=(1, 1, 0, 0))
print(f"BLEU Score: {bleu:.4f}")