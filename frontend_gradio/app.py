import gradio as gr
import requests
import json
from datetime import datetime
import pandas as pd
import os

article_history = []

def generate_article(headline, tone, length):
    if not headline:
        return "Please enter a headline first!", None, None
    
    try:
        response = requests.post(
            "http://localhost:8000/generate-article",
            json={
                "headline": headline,
                "tone": tone.lower(),
                "length": int(length)
            }
        )
        
        if response.status_code == 200:
            article_data = response.json()
            
            global article_history
            article_history.append({
                'headline': headline,
                'generated_at': article_data['generated_at']
            })
            
            formatted_article = f"""# {article_data['headline']}
            
Generated on {article_data['generated_at']}

{article_data['article']}

Word count: {article_data['word_count']}
"""
            
            download_path = f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(download_path, 'w') as f:
                f.write(article_data['article'])
            
            return formatted_article, download_path, len(article_history)
        else:
            return f"Error: {response.status_code} - {response.text}", None, None
    except Exception as e:
        return f"Error generating article: {str(e)}", None, None

def create_ui():
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="indigo", neutral_hue="slate", text_size="lg"), css="""
        .container { max-width: 1200px; margin: 0 auto; }
        .article-container { 
            background-color: #2d3748; 
            color: #f7fafc;
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); 
        }
        #headline { font-size: 16px; }
        .tip-box {
            background-color: #2d3748;
            border-left: 4px solid #4c51bf;
            padding: 10px 15px;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        .gr-button-primary {
            background-color: #4c51bf !important;
        }
        .gr-button-primary:hover {
            background-color: #434190 !important;
        }
    """) as demo:
        gr.Markdown("# 📰 AI News Article Generator")
        gr.Markdown("Transform your headlines into full-length news articles using AI")
        
        with gr.Row():
            with gr.Column(scale=2):
                headline = gr.Textbox(
                    label="Enter Your Headline", 
                    placeholder="Type your headline here...", 
                    elem_id="headline"
                )
                
                with gr.Row():
                    tone = gr.Radio(
                        label="Article Tone",
                        choices=["Formal", "Neutral", "Casual"],
                        value="Neutral"
                    )
                    length = gr.Slider(
                        label="Article Length",
                        minimum=200,
                        maximum=1000,
                        value=500,
                        step=50
                    )
                
                generate_btn = gr.Button("Generate Article", variant="primary")
                
                article_output = gr.Markdown(
                    label="Generated Article", 
                    elem_classes=["article-container"]
                )
                
                download_btn = gr.File(label="Download Article")
                
            with gr.Column(scale=1):
                gr.HTML(
                    """
                    <div class="tip-box">
                    <h2>Tips for Better Results</h2>
                    <ul>
                    <li>Be specific with your headline</li>
                    <li>Include key details (Who, What, Where, When)</li>
                    <li>Choose the appropriate tone for your target audience</li>
                    <li>Adjust length based on your needs</li>
                    </ul>
                    </div>
                    """
                )
                
                gr.Markdown("## Your Analytics")
                articles_count = gr.Number(label="Articles Generated", value=0)
        
        generate_btn.click(
            generate_article,
            inputs=[headline, tone, length],
            outputs=[article_output, download_btn, articles_count]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(share=True)