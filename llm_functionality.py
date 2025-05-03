from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
from typing import Literal

# Initialize models
profanity_model_name = "Dabid/abusive-tagalog-profanity-detection"
privacy_model_name = "roberta-base"

# Load profanity model
profanity_tokenizer = AutoTokenizer.from_pretrained(profanity_model_name)
profanity_model = AutoModelForSequenceClassification.from_pretrained(profanity_model_name)

# Load privacy model
privacy_tokenizer = AutoTokenizer.from_pretrained(privacy_model_name)
privacy_model = AutoModelForSequenceClassification.from_pretrained(privacy_model_name)

# Use GPU if available
device = 0 if torch.cuda.is_available() else -1

# Create classifiers
profanity_classifier = pipeline(
    "text-classification",
    model=profanity_model,
    tokenizer=profanity_tokenizer,
    device=device,
    framework="pt"
)

privacy_classifier = pipeline(
    "text-classification",
    model=privacy_model,
    tokenizer=privacy_tokenizer,
    device=device,
    framework="pt"
)


PROMPT_TEMPLATES = {
    "Profanity Detection": {
        "system": """Detect profanity in debt collection conversations. Flag if the text contains:
        1. Explicit swear words (e.g., "damn", "hell", "crap").
        2. Threats ("Pay or else").
        3. Derogatory terms ("idiot", "fraud").
        4. Aggressive tone ("Listen up!").

        Examples:
        - Text: "Pay your damn bill!" → Label: 1
        - Text: "Can we discuss payment options?" → Label: 0

        Text: "{text}"
        Label:""",
        "label_map": {"LABEL_0": 0, "LABEL_1": 1}
    },

    "Privacy Violation": {
        "system": """Flag privacy violations if:
            1. Financial details (balance, account info) are shared **before** verifying:
            - Full address, DOB, or SSN (last 4 digits).
            2. Verification is skipped or unconfirmed by the customer.

            Examples:
            - No Violation: Agent asks for DOB first, then shares balance. → Label: 0
            - Violation: Agent says, "You owe $300" without verification. → Label: 1

            Text: "{text}"
            Label:""",
            "label_map": {"LABEL_0": 0, "LABEL_1": 1}
    }
}



def analyze_text(text: str, analysis_type: Literal["Profanity Detection", "Privacy Violation"]):
    """Analyses the given text using Profanity and Compliance LLMs."""
    template = PROMPT_TEMPLATES[analysis_type]
    
    if analysis_type == "Profanity Detection":
        # Use the Tagalog-English profanity model directly
        result = profanity_classifier(text, truncation=True, max_length=512)
        return 1 if result[0]['label'] == 'LABEL_1' else 0
    else:
        # Use RoBERTa with prompt engineering for privacy checks
        prompt = template["system"].format(text=text)
        result = privacy_classifier(prompt, truncation=True, max_length=512)
        return template["label_map"][result[0]['label']]

