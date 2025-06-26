---
license: mit
title: Pharmacy Assistant
short_description: Gemini Pharmacy Assistant with Gemini Vision + LangGraph
---
# Handwritten Prescription Reading with Gemini Vision + LangGraph

A Gradio application that uses Gemini Vision and LangGraph agents to extract and process handwritten prescriptions.


Pipeline Process:

![image](https://github.com/user-attachments/assets/9e144fdd-cbed-48f6-945b-bb4ce8e0bb7e)


## Features

- **Vision Processing**: Uses Gemini 1.5 Flash to extract prescription data from images
- **Agent-based Processing**: LangChain agents with tool calling for database operations
- **Database Integration**: SQLite database for pharmacy inventory management
- **Real-time Stock Checking**: Automatic inventory verification and updates

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export GOOGLE_API_KEY="your_api_key_here"
```

3. Run the application:
```bash
python app.py
```

## Deployment

To deploy to Hugging Face Spaces:
```bash
gradio deploy
```

## Usage

Upload a handwritten prescription image and the system will:
1. Extract medicine details using vision AI
2. Calculate required quantities 
3. Check database availability 
4. Clarify Purchase

---

