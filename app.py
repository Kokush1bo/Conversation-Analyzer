import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import streamlit as st
from llm_functionality import analyze_text
import json
import html
from datetime import datetime
from typing import List, Dict
from llm_functionality import analyze_text as llm_analyze
from pattern_matching import pattern_detect_profanity, pattern_detect_compliance_violation


def preprocess_json(data):
    """Handle escaped characters and clean text"""
    processed = []
    for utterance in data:
        clean_text = utterance['text'].encode('utf-8').decode('unicode-escape')
        clean_text = html.unescape(clean_text)
        processed.append({
            **utterance,
            'text': clean_text
        })
    return processed


# UI Setup
st.set_page_config(layout="wide")
st.title("🔍 Profanity & Compliance Detector")


# Initialize session state
if 'analyze_clicked' not in st.session_state:
    st.session_state.analyze_clicked = False


# Sidebar - All controls and file handling
with st.sidebar:
    st.header("Settings & File Upload")
    
    # Analysis parameters
    approach = st.selectbox(
        "Approach",
        ["Pattern Matching", "LLM"],
        index=1
    )
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Profanity Detection", "Privacy Violation"]
    )
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload JSON File",
        type=["json"],
        help="Upload call transcript JSON"
    )
    
    # File handling and preview
    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        
        # File details
        file_details = st.expander("📁 File Details", expanded=True)
        with file_details:
            cols = st.columns(2)
            cols[0].write(f"**Filename:** {uploaded_file.name}")
            cols[1].write(f"**Size:** {uploaded_file.size/1024:.2f} KB")
            st.write(f"**Uploaded:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Full file preview
        preview_expander = st.expander("🔍 Preview Full JSON", expanded=False)
        with preview_expander:
            try:
                raw_data = json.load(uploaded_file)
                st.json(raw_data)
                # Reset file pointer after preview
                uploaded_file.seek(0)
            except Exception as e:
                st.error(f"Preview failed: {str(e)}")
        
        # Analyze button
        st.markdown("---")
        st.session_state.analyze_clicked = st.button(
            "🚀 Analyze Conversation", 
            type="primary",
            use_container_width=True
        )


# Main analysis function
def run_analysis(data, approach, analysis_types):
    results = {
        'agent_profanity': False,
        'customer_profanity': False,
        'privacy_violation': False,
        'metadata': {
            'file_name': uploaded_file.name,
            'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'approach': approach,
            'types': analysis_types
        }
    }
    
    # Privacy check (Agent only)
    if "Privacy Violation" in analysis_types:
        if approach == "Pattern Matching":
            violations = pattern_detect_compliance_violation(data)
            results['privacy_violation'] = len(violations) > 0
        else:
            formatted_conv = "\n".join([f"{u['speaker']}: {u['text']}" for u in data])
            results['privacy_violation'] = llm_analyze(formatted_conv, "Privacy Violation")
    
    # Profanity check
    if "Profanity Detection" in analysis_types:
        if approach == "Pattern Matching":
            profanity_results = pattern_detect_profanity(data)
            results['agent_profanity'] = len(profanity_results.get("Agent", [])) > 0
            results['customer_profanity'] = len(profanity_results.get("Borrower", [])) > 0
        else:
            for utterance in data:
                speaker = utterance['speaker'].lower()
                text = utterance['text']
                is_profane = llm_analyze(text, "Profanity Detection")
                
                if is_profane:
                    if speaker == "agent":
                        results['agent_profanity'] = True
                    else:
                        results['customer_profanity'] = True
    
    return results

# Main display area
if uploaded_file and st.session_state.analyze_clicked:
    try:
        raw_data = json.load(uploaded_file)
        data = preprocess_json(raw_data)
        
        if not isinstance(data, list):
            st.error("Invalid format: Expected list of utterances")
            st.stop()
        
        with st.spinner("Analyzing conversation..."):
            results = run_analysis(data, approach, analysis_type)
        
        # Display results
        st.success("🎉 Analysis Complete!")
        st.divider()
        
        # Profanity Results
        if "Profanity Detection" in analysis_type:
            st.subheader("Profanity Analysis")
            cols = st.columns(2)
            cols[0].metric(
                "Agent Profanity", 
                "⚠️ Found" if results['agent_profanity'] else "✅ Clean",
                help="Indicates if agent used profane language"
            )
            cols[1].metric(
                "Customer Profanity", 
                "⚠️ Found" if results['customer_profanity'] else "✅ Clean",
                help="Indicates if customer used profane language"
            )
        
        # Privacy Results (Agent only)
        if "Privacy Violation" in analysis_type:
            st.subheader("Privacy Compliance")
            st.metric(
                "Agent Privacy Violation", 
                "⚠️ Found" if results['privacy_violation'] else "✅ Clean",
                help="Indicates if agent shared sensitive info without verification"
            )
    
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
else:
    st.info("ℹ️ Upload a JSON file and click 'Analyze Conversation' to begin")

