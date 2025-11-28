import google.generativeai as genai
import os

class LLMService:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Gemini API Key is missing. Please check your .env file.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        self.system_prompt = """You are a helpful weather assistant for the NextWeather Dashboard.
        You have access to real-time weather data provided in the context.
        
        GUIDELINES:
        1. Answer questions accurately based ONLY on the provided context.
        2. If the context doesn't contain the answer, say "I don't have that information in the current data."
        3. Be concise and conversational.
        4. Use Fahrenheit for temperature and mph for wind unless asked otherwise.
        5. If asked about hazards, prioritize safety warnings.
        
        CONTEXT STRUCTURE:
        The user will provide a context block containing:
        - Current Conditions
        - Forecast Summary
        - Active Hazards
        
        Use this to answer the user's question.
        """

    def generate_response(self, query, context, history=[]):
        """Generates a response using Gemini."""
        
        # Format history for Gemini (optional, for now we just use single turn with context)
        # Gemini supports chat history, but for simplicity we'll append context to the prompt each time
        # or use the chat session if we want multi-turn.
        
        full_prompt = f"""{self.system_prompt}

DATA CONTEXT:
{context}

USER QUESTION:
{query}

ASSISTANT RESPONSE:"""

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"I encountered an error generating a response: {str(e)}"
