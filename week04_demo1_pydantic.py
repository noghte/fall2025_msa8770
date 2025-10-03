from pydantic import BaseModel, Field, ValidationError
from enum import Enum

class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"

class ReviewAnalysis(BaseModel):
    review:str = Field(description="the review text")
    # sentiment:str = Field("must be positive, neutral, or negative")
    sentiment:Sentiment = Field("must be positive, neutral, or negative")
    confidence:float =Field("confidence between 0 to 1", ge=0, le=1)

example1 = {
    "review": "Great product",
    "sentiment": "positive",
    "confidence": 0.98
}

# result = ReviewAnalysis(review=example1["review"],
#     sentiment=example1["sentiment"],
#     confidence=example1["confidence"])

result = ReviewAnalysis(**example1)

print("All:", result)
print("Sentiment:", result.sentiment)

example2 = {
    "review": "Great product",
    "sentiment": "wrong",
    "confidence": 1
}
result2 = ""
try:
    result2 = ReviewAnalysis(**example2)
except ValidationError as e:
    print("cannot validation")

print(result2)