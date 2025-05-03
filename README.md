---
title: "Debt Collection Compliance Analyzer"
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker  # or "gradio" if you're not using Docker
sdk_version: "20.0.0"
app_file: app.py
pinned: false
---

# Debt Collection Conversation Analyzer

A Streamlit application that analyzes debt collection conversations for:
- Profanity detection (agents/borrowers)
- Privacy compliance violations

## Features
- Pattern matching (regex) and LLM analysis
- YAML file input processing
- Interactive visualizations

## How to Use
1. Upload a YAML conversation file
2. Select analysis type (Profanity/Privacy)
3. Choose approach (Pattern Matching/LLM)
4. View results and metrics

## Requirements
See [requirements.txt](./requirements.txt) for Python dependencies