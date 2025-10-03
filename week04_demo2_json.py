# pip install --upgrade langchain langchain-openai langchain-core
from pydantic import BaseModel, Field, ValidationError
from enum import Enum
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"

class ReviewAnalysis(BaseModel):
    review:str = Field(description="the review text")
    # sentiment:str = Field("must be positive, neutral, or negative")
    sentiment:Sentiment = Field("must be positive, neutral, or negative")
    confidence:float =Field("confidence between 0 to 1", ge=0, le=1)

df = pd.read_csv("amazon_reviews.csv", nrows=2)
review = df["reviewText"].iloc[1]

parser = JsonOutputParser(pydantic_object=ReviewAnalysis)

prompt = PromptTemplate(
    template="Analyze the review and return a JSON. Review: \n {review} \n Instructions: \n {format_instructions}",
    input_variables=["review"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)
llm = ChatOpenAI(
    base_url="http://10.230.100.240:17020/v1",
    api_key="not-needed",
    model="command-r:latest", # phi3:latest
    temperature=0,
)

chain = prompt | llm | parser
result = chain.invoke({"review":review})

print("Parsed object:", result)
print(result["review"])
print(result["sentiment"])
print(result["confidence"])
