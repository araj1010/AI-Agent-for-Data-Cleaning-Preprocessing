import sys
import os
import pandas as pd
import io
import aiohttp
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.ai_agent import AIAgent
from scripts.data_cleaning import DataCleaning

app = FastAPI()

# Initialize cleaners
ai_agent = AIAgent()
cleaner = DataCleaning()


def parse_ai_result(ai_result, fallback_df):
    if isinstance(ai_result, str) and ai_result.startswith("Error:"):
        print(f"AI returned an error: {ai_result}; using rule-based cleaned data.")
        return fallback_df.to_dict(orient='records')

    if not isinstance(ai_result, str) or not ai_result.strip():
        print("AI returned empty or invalid output; using rule-based cleaned data.")
        return fallback_df.to_dict(orient='records')

    try:
        from io import StringIO
        df_ai_cleaned = pd.read_csv(StringIO(ai_result))
        output = df_ai_cleaned.to_dict(orient='records')
        if output == [] and len(fallback_df) > 0:
            print("AI returned empty CSV result; falling back to rule-based cleaned data.")
            return fallback_df.to_dict(orient='records')
        return output
    except Exception as exc:
        print(f"AI parsing failed: {exc}; using rule-based cleaned data.")
        return fallback_df.to_dict(orient='records')


# ---------------- CSV / Excel Cleaning ---------------- #
@app.post("/clean-data")
async def clean_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_extension = file.filename.split('.')[-1]

        # Read file
        if file_extension == 'csv':
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        elif file_extension == 'xlsx':
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(400, "Unsupported format. Use CSV or Excel.")

        print("Original rows:", len(df))

        # Step 1: Rule-based cleaning
        df_cleaned = cleaner.clean_data(df)
        print("After rule cleaning:", len(df_cleaned))

        # Step 2: AI cleaning
        ai_result = ai_agent.process_data(df_cleaned)
        print("AI OUTPUT:", ai_result)

        output = parse_ai_result(ai_result, df_cleaned)
        return {"cleaned_data": output}

    except Exception as e:
        raise HTTPException(500, str(e))


# ---------------- Database Cleaning ---------------- #
class DBQuery(BaseModel):
    db_url: str
    query: str


@app.post("/clean-db")
async def clean_db(query: DBQuery):
    try:
        from sqlalchemy import text
        engine = create_engine(query.db_url)
        with engine.connect() as conn:
            df = pd.read_sql(text(query.query), conn)

        df_cleaned = cleaner.clean_data(df)
        ai_result = ai_agent.process_data(df_cleaned)

        output = parse_ai_result(ai_result, df_cleaned)
        return {"cleaned_data": output}

    except Exception as e:
        raise HTTPException(500, str(e))


# ---------------- API Cleaning ---------------- #
class APIRequest(BaseModel):
    api_url: str


@app.post("/clean-api")
async def clean_api(api_request: APIRequest):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_request.api_url) as response:
                if response.status != 200:
                    raise HTTPException(400, f"API failed: {response.status}")

                data = await response.json()

        # Normalize nested JSON into flat table format
        if isinstance(data, dict):
            if 'data' in data and isinstance(data['data'], list):
                data = data['data']
            else:
                data = [data]

        df = pd.json_normalize(data, sep='.')
        df_cleaned = cleaner.clean_data(df)
        ai_result = ai_agent.process_data(df_cleaned)

        output = parse_ai_result(ai_result, df_cleaned)
        return {"cleaned_data": output}

    except Exception as e:
        raise HTTPException(500, str(e))


# ---------------- Run Server ---------------- #
if __name__ == "__main__":
    import uvicorn
    # uvicorn needs an import string for the app when using reload=True
    uvicorn.run("scripts.backend:app", host="127.0.0.1", port=8000, reload=True)