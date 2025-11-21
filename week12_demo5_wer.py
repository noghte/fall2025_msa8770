from jiwer import wer, cer

# Word Error Rate
reference = "the cat sat on the mat"
hypothesis = "the dog sat on mat"

wer_score = wer(reference, hypothesis)
print(f"WER: {wer_score:.3f}")  # 0.333 (33.3%)

# Character Error Rate (for finer-grained analysis)
cer_score = cer(reference, hypothesis)
print(f"CER: {cer_score:.3f}")

# Multiple references
# references = ["the cat sat on the mat", 
#               "a cat was sitting on the mat"]
# hypotheses = ["the dog sat on mat",
#               "a cat sat on the rug"]

# wer_score_multi = wer(references, hypotheses)
# print(f"Average WER: {wer_score_multi:.3f}")