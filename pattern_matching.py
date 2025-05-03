import re
from typing import List, Dict, Union
from collections import defaultdict

# Enhanced profanity word list with variations
PROFANE_WORDS = [
    # Base words
    r'damn', r'hell', r'shit', r'fuck', r'bastard', r'asshole', r'crap',
    r'dick', r'piss', r'slut', r'bitch', r'motherfucker', r'nigger',
    
    # Common variations and misspellings
    r'f\*ck', r'f\*\*k', r'sh\*t', r'b\*tch', r'a\*hole', r'd\*mn',
    r'f\*\*\*', r's\*\*t', r'f\*\*', r'f\*\*\*ing', r'f\*\*king',
    r'fuk', r'shitty', r'fucking', r'fcked', r'fcker'
]

# Compile more comprehensive regex pattern
PROFANITY_REGEX = re.compile(
    r'(?:^|\b)(?:' + '|'.join(PROFANE_WORDS) + r')(?:$|\b)',
    re.IGNORECASE
)

def pattern_detect_profanity(conversation: List[Dict[str, Union[str, int]]]) -> Dict[str, List[Dict]]:
    """
    Enhanced profanity detection with better pattern matching.
    
    Args:
        conversation: List of utterance dictionaries with 'speaker', 'text', etc.
        
    Returns:
        Dictionary with 'Agent' and 'Borrower' keys containing flagged utterances.
    """
    result = defaultdict(list)
    
    for utterance in conversation:
        speaker = utterance.get("speaker", "").strip().lower()
        text = utterance.get("text", "")
        
        if not text:
            continue
            
        # Find all profanity matches
        matches = PROFANITY_REGEX.finditer(text)
        if matches:
            # Add match information to the utterance
            matched_words = [m.group() for m in matches]
            flagged_utterance = utterance.copy()
            flagged_utterance["matched_words"] = matched_words
            
            # Categorize by speaker
            if "agent" in speaker:
                result["Agent"].append(flagged_utterance)
            elif "borrower" in speaker:
                result["Borrower"].append(flagged_utterance)
                
    return dict(result)


# Enhanced sensitive info and verification patterns
SENSITIVE_PATTERNS = [
    r'\baccount\s*(?:number|#)?\s*[:=]?\s*\d+',  # Account numbers
    r'\b(?:balance|amount due|outstanding|payment due)\s*[:=]?\s*\$\d+',  # Monetary amounts
    r'\b(?:credit|debit)\s*card\s*(?:number|#)?\s*[:=]?\s*\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',  # Card numbers
    r'\b(?:ssn|social security)\s*(?:number|#)?\s*[:=]?\s*\d{3}[-\s]?\d{2}[-\s]?\d{4}'  # SSN
]

VERIFICATION_PATTERNS = [
    r'\b(?:verify|verification|confirm)\b.*\b(?:identity|yourself)\b',
    r'\b(?:date of birth|dob)\s*[:=]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
    r'\b(?:address)\s*[:=]?\s*(?:\d+\s+[\w\s]+,\s*[\w\s]+,\s*[A-Z]{2}\s*\d{5})',
    r'\b(?:social security|ssn)\s*(?:number|#)?\s*[:=]?\s*\d{3}[-\s]?\d{2}[-\s]?\d{4}',
    r'\b(?:last\s*4\s*digits\s*of\s*ssn)\s*[:=]?\s*\d{4}'
]

# Compile patterns for better performance
SENSITIVE_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in SENSITIVE_PATTERNS]
VERIFICATION_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in VERIFICATION_PATTERNS]

def pattern_detect_compliance_violation(conversation: List[Dict[str, Union[str, int]]]) -> List[Dict]:
    """
    Enhanced compliance violation detection with better pattern matching.
    
    Args:
        conversation: List of utterance dictionaries with 'speaker', 'text', etc.
        
    Returns:
        List of violating utterances with detected sensitive info and verification status.
    """
    violations = []
    verified = False
    verification_attempted = False
    
    for utterance in conversation:
        speaker = utterance.get("speaker", "").strip().lower()
        text = utterance.get("text", "")
        
        if speaker != "agent" or not text:
            continue
            
        # Check for verification attempts
        if not verified:
            for pattern in VERIFICATION_REGEX:
                if pattern.search(text):
                    verification_attempted = True
                    # Check if verification was successful (simplified)
                    if "correct" in text.lower() or "match" in text.lower():
                        verified = True
                    break
                    
        # Check for sensitive information
        sensitive_info = []
        for pattern in SENSITIVE_REGEX:
            match = pattern.search(text)
            if match:
                sensitive_info.append(match.group())
                
        if sensitive_info and not verified:
            flagged_utterance = utterance.copy()
            flagged_utterance["sensitive_info"] = sensitive_info
            flagged_utterance["verification_status"] = {
                "verified": verified,
                "attempted": verification_attempted
            }
            violations.append(flagged_utterance)
            
    return violations

