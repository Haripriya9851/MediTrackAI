# PharmAssist

## Features
**Better Prescription Understanding:** Accurate transcript reading,for dosage, quantity, days extraction with Gemini LLM

**High Reasoning:** Used Chain-of-Thought prompt engineering technique to clean, organize and extract data in structured JSON format.

**Prescription style variability:** Handled via repeated testing and fine-tuning prompts.

**Dynamic SQL Query Generation :** Used Langchain Tool calling to communicate and update SQLLite DB

## Setup

Install dependencies:
```pip install -r requirements.txt```

Set up environment variables:
```export GOOGLE_API_KEY="your_api_key_here" ```

Run the application:
```python app.py```

Deployment
To deploy to Hugging Face Spaces:
```gradio deploy```

## Usage

**Upload a handwritten prescription image and the system will:**

- Extract medicine details using vision AI
- Calculate required quantities
- Check database availability
- Clarify Purchase

