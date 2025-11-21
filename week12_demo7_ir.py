from ranx import Qrels, Run, evaluate

# Query Relevance Judgments (ground truth / baseline)
qrels = Qrels({
    "python-list-comprehension": {
        "How to use list comprehension in Python": 1,
        "An introduction to list comprehensions": 1,
        "Advanced list comprehension tricks": 1
    }
})

run = Run({
    "python-list-comprehension": {
        "How to use list comprehension in Python": 3,           # rank 1
        "Python loops explained": 2,                            # rank 2 (non-relevant)
        "An introduction to list comprehensions": 1             # rank 3
        # Missing: "Advanced list comprehension tricks"
    }
})

metrics = ["map", "mrr"]

results = evaluate(qrels, run, metrics)

print(f"MAP: {results['map']:.2f}")
print(f"MRR: {results['mrr']:.2f}")