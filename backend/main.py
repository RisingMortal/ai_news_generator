from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import Optional
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
# print(os.getenv('GOOGLE_API_KEY'))


app = FastAPI(
    title="News Article Generator API",
    description="API for generating news articles from headlines using Gemini",
    version="1.0.0"
)

class HeadlineRequest(BaseModel):
    headline: str
    tone: Optional[str] = "neutral"
    length: Optional[int] = 500

class ArticleResponse(BaseModel):
    headline: str
    article: str
    generated_at: str
    word_count: int

def create_prompt(headline: str) -> str:
    return f"""Generate a news article based on the following headline. 
    Make sure the article is factual, well-structured.
    
    Headline: {headline}
    
    Please follow these guidelines:
    - Write in a journalistic style
    - Include relevant details and context
    - Maintain objectivity
    - Use clear and concise language
    - Follow proper news article structure (lead paragraph, body, conclusion)
    """

@app.post("/generate-article", response_model=ArticleResponse)
async def generate_article(request: HeadlineRequest):
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel("tunedModels/new-model-uxen6rexyhu7")
        
        # Create the prompt
        prompt = create_prompt(request.headline)
        
        # Generate the article
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': request.length * 4  # Approximate conversion from words to tokens
            }
        )
        
        # Extract and clean the generated text
        article = response.text.strip()
        # print(article)
        
        # Calculate word count
        word_count = len(article.split())
        
        return ArticleResponse(
            headline=request.headline,
            article=article,
            generated_at=datetime.now().isoformat(),
            word_count=word_count
        )
    except Exception as e:
        # print(str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error generating article: {str(e)}"
        )

# Optional: Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "gemini-pro"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)