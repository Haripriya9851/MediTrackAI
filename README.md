# PharmAssist

## Features
**Vision Processing:** Uses Gemini 1.5 Flash to extract prescription data from images

**Agent-based Processing:** LangChain agents with tool calling for database operations

**Database Integration:** SQLite database for pharmacy inventory management

**Real-time Stock Checking:** Automatic inventory verification and updates

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

