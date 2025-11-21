from rouge_score import rouge_scorer

# Initialize scorer with desired metrics
scorer = rouge_scorer.RougeScorer(
    ['rouge1', 'rouge2', 'rougeL'], 
    use_stemmer=True
)

# Example 1: Single summary evaluation
reference = "The cat sat on the mat and slept peacefully"
candidate = "The cat slept on the mat"

scores = scorer.score(reference, candidate)

print("ROUGE-1:")
print(f"  Precision: {scores['rouge1'].precision:.3f}")
print(f"  Recall:    {scores['rouge1'].recall:.3f}")
print(f"  F1:        {scores['rouge1'].fmeasure:.3f}")

print("\nROUGE-2:")
print(f"  Precision: {scores['rouge2'].precision:.3f}")
print(f"  Recall:    {scores['rouge2'].recall:.3f}")
print(f"  F1:        {scores['rouge2'].fmeasure:.3f}")

print("\nROUGE-L:")
print(f"  Precision: {scores['rougeL'].precision:.3f}")
print(f"  Recall:    {scores['rougeL'].recall:.3f}")
print(f"  F1:        {scores['rougeL'].fmeasure:.3f}")

# Example 2: Batch evaluation
# references = [
#     "The cat sat on the mat",
#     "The dog played in the park"
# ]
# candidates = [
#     "The cat is on the mat",
#     "A dog played at the park"
# ]

# avg_rouge1, avg_rouge2, avg_rougeL = 0, 0, 0

# for ref, cand in zip(references, candidates):
#     scores = scorer.score(ref, cand)
#     avg_rouge1 += scores['rouge1'].fmeasure
#     avg_rouge2 += scores['rouge2'].fmeasure
#     avg_rougeL += scores['rougeL'].fmeasure

# n = len(references)
# print(f"\nAverage ROUGE-1: {avg_rouge1/n:.3f}")
# print(f"Average ROUGE-2: {avg_rouge2/n:.3f}")
# print(f"Average ROUGE-L: {avg_rougeL/n:.3f}")