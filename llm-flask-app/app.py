import os
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import logging
import pandas as pd

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    """Health check endpoint"""
    df = pd.read_csv("TaylorSwift.csv", nrows=4)

    return jsonify({
        "status": "healthy",
        "message": "LLM Flask API is running",
        "version": "1.0.0",
        "lyrics": df.iloc[0]["Lyric"][:50]
    })


@app.route('/api/chat/', methods=['POST'])
def chat():
    """
    Chat endpoint that calls OpenAI API
    
    Expected JSON payload:
    {
        "message": "Your question here",
        "model": "gpt-4o-mini",  # optional
        "temperature": 0.7  # optional
    }
    """
    try:
        # Validate request
        if not request.json:
            return jsonify({
                "error": "Invalid request",
                "message": "Request body must be JSON"
            }), 400
        
        message = request.json.get('message')
        if not message:
            return jsonify({
                "error": "Missing field",
                "message": "The 'message' field is required"
            }), 400
        
        # Get optional parameters
        model = request.json.get('model', 'gpt-4o-mini')
        temperature = request.json.get('temperature', 0.7)
        
        # Log the request
        logger.info(f"Processing chat request with model: {model}")
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Whatever users says, repeat it in a funny way!"},
                {"role": "user", "content": message}
            ],
            temperature=temperature,
            max_tokens=500
        )
        
        # Extract response
        assistant_message = response.choices[0].message.content
        
        # Log success
        logger.info("Successfully generated response")
        
        return jsonify({
            "response": assistant_message,
            "model": model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)