from transformers import (
    pipeline,
    BertForSequenceClassification,
    BertTokenizer,
    AutoModelForSequenceClassification,
    AutoTokenizer
)
import torch
from typing import Literal

# Configuration
MODEL_PATHS = {
    "profanity": "./bert_profanity_model",  # Your fine-tuned BERT model
    "privacy": "roberta-base"  # Default privacy model
}

# Load models with error handling
try:
    # Load fine-tuned BERT profanity model
    profanity_tokenizer = BertTokenizer.from_pretrained(MODEL_PATHS["profanity"])
    profanity_model = BertForSequenceClassification.from_pretrained(MODEL_PATHS["profanity"])
    
    # Load privacy model
    privacy_tokenizer = AutoTokenizer.from_pretrained(MODEL_PATHS["privacy"])
    privacy_model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATHS["privacy"])
    
except Exception as e:
    raise RuntimeError(f"Failed to load models: {str(e)}")

# Device configuration
device = 0 if torch.cuda.is_available() else -1

# Initialize pipelines
classifiers = {
    "Profanity Detection": pipeline(
        "text-classification",
        model=profanity_model,
        tokenizer=profanity_tokenizer,
        device=device,
        framework="pt",
        truncation=True,
        max_length=512
    ),
    "Privacy Violation": pipeline(
        "text-classification",
        model=privacy_model,
        tokenizer=privacy_tokenizer,
        device=device,
        framework="pt",
        truncation=True,
        max_length=512
    )
}

PROMPT_TEMPLATES = {
    "Profanity Detection": {
        "description": "Detects inappropriate language in financial conversations",
        "label_map": {"LABEL_0": "Clean", "LABEL_1": "Profanity"}
    },
    "Privacy Violation": {
        "system": """Analyze for privacy violations:
        1. Check if financial details are shared before verification
        2. Verify if proper authentication was skipped
        Text: "{text}"
        Label:""",
        "label_map": {"LABEL_0": "Compliant", "LABEL_1": "Violation"}
    }
}

def analyze_text(text: str, analysis_type: Literal["Profanity Detection", "Privacy Violation"]):
    """
    Analyze text using appropriate model.
    
    Args:
        text: Input text to analyze
        analysis_type: Type of analysis to perform
        
    Returns:
        dict: {
            'label': str, 
            'score': float,
            'model': str
        }
    """
    if not text.strip():
        return {"error": "Empty input text"}
    
    try:
        # Profanity detection (uses your fine-tuned BERT directly)
        if analysis_type == "Profanity Detection":
            result = classifiers[analysis_type](text)
            return {
                'label': PROMPT_TEMPLATES[analysis_type]["label_map"][result[0]['label']],
                'score': float(result[0]['score']),
                'model': "Fine-tuned BERT"
            }
        
        # Privacy check (uses prompt engineering with RoBERTa)
        else:
            prompt = PROMPT_TEMPLATES[analysis_type]["system"].format(text=text)
            result = classifiers[analysis_type](prompt)
            return {
                'label': PROMPT_TEMPLATES[analysis_type]["label_map"][result[0]['label']],
                'score': float(result[0]['score']),
                'model': "RoBERTa-base"
            }
            
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}