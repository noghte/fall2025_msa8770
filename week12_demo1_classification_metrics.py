from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    classification_report,
)
import numpy as np

y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1])
y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 1])

accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

print(f"Accuracy:  {accuracy:.3f}")  # 0.800
print(f"Precision: {precision:.3f}") # 0.833
print(f"Recall:    {recall:.3f}")    # 0.833
print(f"F1 Score:  {f1:.3f}")        # 0.833

# For multi-class
y_true_multi = ['pos', 'neg', 'neu', 'pos', 'neg', 'pos']
y_pred_multi = ['pos', 'neg', 'neu', 'neu', 'neg', 'pos']

# Get detailed report
print(classification_report(y_true_multi, y_pred_multi))