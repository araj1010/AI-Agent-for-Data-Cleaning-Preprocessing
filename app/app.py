import streamlit as st
import requests
import pandas as pd
import json
from io import StringIO

# Backend FastAPI URL (must be running)
FASTAPI_URL = "http://127.0.0.1:8000"

# Page config
st.set_page_config(page_title="AI Data Cleaning", layout="wide")

# Sidebar for source selection
st.sidebar.header("🤖 Data Source Selection")
data_source = st.sidebar.radio("Select Data Source:", ["CSV/Excel", "Database Query", "API Data"], index=0)

#Main Title
st.markdown("""# 🧹 **AI-Powered Data Cleaning & Preprocessing**
            *Clean your data effortlessly using AI-powered processing!*""")

# Data source handling
if data_source == "CSV/Excel":
    st.subheader("Upload CSV or Excel File")
    uploaded_file = st.file_uploader("Choose CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1]
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.write("📊 Raw Data Preview")
        st.dataframe(df)
        
        if st.button("🧹 Clean Data"):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(f"{FASTAPI_URL}/clean-data", files=files)

                if response.status_code == 200:
                    st.subheader("✅ Raw API Response (For Debugging)")
                    st.json(response.json())  # Show raw response for debugging
                
                    #parse cleaned data properly
                    try:
                        cleaned_data_raw = response.json()["cleaned_data"]
                        if isinstance(cleaned_data_raw, str):
                            cleaned_data = pd.DataFrame(json.loads(cleaned_data_raw))
                        else:
                            cleaned_data = pd.DataFrame(cleaned_data_raw)
                        
                        st.subheader("✅ Cleaned Data:")
                        st.dataframe(cleaned_data)
                    except Exception as e:
                        st.error(f"Error parsing cleaned data: {e}")
                else:
                    st.error("Failed to clean data.")

# Handle Database Query                           
elif data_source == "Database Query":
    st.subheader("Enter Database Query")
    db_url = st.text_input("Database URL:", value="postgresql://postgres:test1234@localhost:5432/postgres")
    query = st.text_area("Enter SQL Query:", value="SELECT * FROM my_table;")
    
    if st.button("🔍 Fetch & Clean Data"):
        response = requests.post(f"{FASTAPI_URL}/clean-db", json={  "db_url": db_url, "query": query})
        
        if response.status_code == 200:
            st.subheader("✅ Raw API Response (For Debugging)")
            st.json(response.json())  # Show raw response for debugging
            try:
                cleaned_data_raw = response.json()["cleaned_data"]
                if isinstance(cleaned_data_raw, str):
                    cleaned_data = pd.DataFrame(json.loads(cleaned_data_raw))
                else:
                    cleaned_data = pd.DataFrame(cleaned_data_raw)
                
                st.subheader("✅ Cleaned Data from Database")
                st.dataframe(cleaned_data)
            except Exception as e:
                st.error(f"Error parsing cleaned data: {e}")
        else:
            st.error("Failed to fetch and clean data from database.")

# Handle API Data
elif data_source == "API Data":
    st.subheader("Fetch Data from API")
    api_url = st.text_input("Enter API Endpoint:", value="https://jsonplaceholder.typicode.com/posts")
    
    if st.button("📡 Fetch & Clean"):
        response = requests.post(f"{FASTAPI_URL}/clean-api", json={"api_url": api_url})
        if response.status_code == 200:
            st.subheader("✅ Raw API Response (For Debugging)")
            st.json(response.json())
            try:
                cleaned_data_raw = response.json()["cleaned_data"]
                if isinstance(cleaned_data_raw, str):
                    cleaned_data = pd.DataFrame(json.loads(cleaned_data_raw))
                else:
                    cleaned_data = pd.DataFrame(cleaned_data_raw)

                st.subheader("✅ Cleaned Data from API")
                st.dataframe(cleaned_data)
            except Exception as e:
                st.error(f"Error parsing cleaned data: {e}")
        else:
            st.error("Failed to fetch and clean data from API.")

# Footer
st.markdown("""---  
            ** Made with ❤️ by Anand Raj for automated data cleaning **""")