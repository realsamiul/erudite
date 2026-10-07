import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from typing import List, Dict, Any
from services.discovery import SearchChunk

_initialized = False
_pro_model = None
_flash_model = None

def _init_models():
    global _initialized, _pro_model, _flash_model
    if _initialized:
        return
    
    project_id = os.environ.get("PROJECT_ID", "project-a1f62154-a7ad-4b37-93b")
    # For gemini-3.5-flash, global location is required in this project environment
    region = "global"
    
    vertexai.init(project=project_id, location=region)
    
    # Load model dynamically from environment variable or default to gemini-3.5-flash
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
    print(f"[Gemini] Initializing model '{model_name}' in region '{region}'...")
    
    _pro_model = GenerativeModel(
        model_name,
        generation_config=GenerationConfig(temperature=0.1)
    )
    _flash_model = GenerativeModel(
        model_name,
        generation_config=GenerationConfig(temperature=0.0)
    )
    _initialized = True

async def synthesize_counselor_response(
    query: str,
    retrieved_chunks: List[SearchChunk]
) -> Dict[str, Any]:
    """
    Synthesizes the retrieved segments into a beautiful, scannable, and 
    empathetic admissions counselor response with structured visual metadata.
    """
    _init_models()
    
    # Format the source snippets
    context_str = ""
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        context_str += f"[Source {idx}] ({chunk.source_display_name}):\n{chunk.text}\n\n"
        
    system_persona = (
        "You are the deeply compassionate, highly authoritative, and realistic elder sibling "
        "or specialized college admissions counselor who has successfully navigated the US admissions process "
        "and is protecting high-need Bangladeshi applicants. Speak with quiet, data-backed confidence. "
        "Avoid sterile corporate AI preambles and generic boilerplate. Your output must be returned "
        "strictly in a clean, visual, and scannable JSON schema. Do not output raw paragraphs of text. "
        "Use structured, spacious, and believable cards, charts, and bullet points."
    )
    
    user_prompt = f"""
    Contextual Grounded Data:
    {context_str}
    
    Student Query:
    {query}
    
    Generate your responsive counseling payload matching the JSON structure below. 
    You must calculate appropriate metric cards, pie/bar chart slices (based on the real CDS percentages in the context, e.g. 77.9% aided vs 22.1% full-pay), 
    and provide detailed, reality-grounded audit feedback regarding EFC warning, national curriculum (SSC/HSC) gates, and feeder pipelines.
    
    Required JSON Schema output:
    {{
        "greeting": "Warm, reassuring welcome addressing the query...",
        "answer": "Concise, Markdown-supported grounded answer outlining the primary strategic advice...",
        "quick_stats": [
            {{"label": "Key Label 1", "value": "$XX,XXX", "badge_type": "success|info|warning|danger"}},
            {{"label": "Key Label 2", "value": "XX.X%", "badge_type": "success|info|warning|danger"}}
        ],
        "charts": [
            {{
                "type": "pie|bar|gauge",
                "title": "Descriptive Visualization Title",
                "data": {{"Slices / Metrics Name": 75.0, "Alternative Slice": 25.0}}
            }}
        ],
        "audit_feedback": {{
            "loopholes": "Rigorous reality check highlighting if the average aid award doesn't match the marketed headline or if loans are hidden in the fine-print.",
            "curriculum_warnings": "Specific guidance on whether this school ignores Bangladesh SSC/HSC national curriculum or requires Cambridge A-Levels.",
            "pipeline_alerts": "Honest alert regarding whether this school is familiarity-biased toward specific Dhaka pipeline high schools like Scholastica."
        }}
    }}
    """
    
    try:
        # Request a JSON output format from Gemini
        response = _pro_model.generate_content(
            [system_persona, user_prompt],
            generation_config=GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        payload = json.loads(response.text)
        return payload
    except Exception as e:
        print(f"[Gemini] Generation failed or returned invalid JSON: {e}")
        # Secure fallback payload to prevent server crashes
        return {
            "greeting": "Let's look at this together.",
            "answer": f"I received your question regarding: '{query}'. However, the model is currently warming up. Let me guide you on where to look in the console.",
            "quick_stats": [{"label": "Status", "value": "Online", "badge_type": "info"}],
            "charts": [],
            "audit_feedback": {
                "loopholes": "Indexing in progress. High-need packages must be verified directly against Section H6 in the common data set.",
                "curriculum_warnings": "SSC/HSC evaluation requires school-profile context sheets.",
                "pipeline_alerts": "No pipeline data is loaded yet."
            }
        }
