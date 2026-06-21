import os
import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel

from google import genai
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("Gemini API key is missing. Set it in .env")

client = genai.Client(api_key=gemini_api_key)


# -----------------------------
# State model
# -----------------------------
class CleaningState(BaseModel):
    input_text: str
    structured_response: str = ""


# -----------------------------
# AI Agent
# -----------------------------
class AIAgent:
    def __init__(self):
        self.graph = self.create_graph()

    def create_graph(self):
        graph = StateGraph(CleaningState)

        def agent_logic(state: CleaningState) -> CleaningState:
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=state.input_text
                )
                content = response.text if response else "No response"
            except Exception as e:
                content = f"Error: {str(e)}"

            return CleaningState(
                input_text=state.input_text,
                structured_response=content
            )

        graph.add_node("cleaning_agent", agent_logic)
        graph.set_entry_point("cleaning_agent")
        graph.add_edge("cleaning_agent", END)

        return graph.compile()

    def process_data(self, df: pd.DataFrame, batch_size: int = 20):
        cleaned_responses = []

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]

            prompt = f"""
You are an AI data cleaning agent.

Dataset:
{batch.to_string()}

Tasks:
- Handle missing values
- Remove duplicates
- Fix data types

Return ONLY cleaned data in strict CSV format.

Rules:
- No explanation
- No extra text
- Only raw CSV

Example:
name,age
A,23
B,25
"""

            state = CleaningState(input_text=prompt)
            result = self.graph.invoke(state)

            if isinstance(result, dict):
                result = CleaningState(**result)

            cleaned_responses.append(result.structured_response)

        return "\n\n".join(cleaned_responses)