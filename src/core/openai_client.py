from google.colab import userdata
from openai import OpenAI

def get_openai_client():
    api_key = userdata.get("OpenAIApi")

    if not api_key:
        raise ValueError("OpenAI API key missing")

    return OpenAI(api_key=api_key)