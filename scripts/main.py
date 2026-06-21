# scripts/main.py - Full pipeline orchestrator
from data_ingestions import DataIngestion  # Data loading from sources  
from data_cleaning import DataCleaning    # Rule-based cleaning  
from ai_agent import AIAgent              # AI-powered enhancement  

# Database config (matches test_postgres_connection.py)
DB_USER = "postgres"
DB_PASSWORD = "test1234"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize components
ingestion = DataIngestion(db_url=DB_URL)
cleaner = DataCleaning()
ai_agent = AIAgent()  

print("🚀 Testing Full Data Cleaning Pipeline\n")

# 1. CSV Processing
print("📄 Processing CSV...")
df_csv = ingestion.load_csv("data/sample_data.csv")
if df_csv is not None:
    print("\n Cleaning CSV Data...")
    df_csv = cleaner.clean_data(df_csv)
    df_csv = ai_agent.process_data(df_csv)
    print("✅ CSV Cleaned Data:\n", df_csv.head())
    print("-" * 50)  

# 2. Excel Processing
print("📊 Processing Excel...")
df_excel = ingestion.load_excel("data/sample_data.xlsx")
if df_excel is not None:
    print("\n Cleaning Excel Data...")
    df_excel = cleaner.clean_data(df_excel)
    df_excel = ai_agent.process_data(df_excel)
    print("✅ Excel Cleaned Data:\n", df_excel.head())
    print("-" * 50)

# 3. Database Processing
print("🗄️ Processing Database...")
df_db = ingestion.load_from_database("SELECT * FROM my_table")
if df_db is not None:
    print("\n Cleaning Database Data...")
    df_db = cleaner.clean_data(df_db)
    df_db = ai_agent.process_data(df_db)
    print("✅ DB Cleaned Data:\n", df_db.head())
    print("-" * 50)

# 4. API Processing
print("🌐 Processing API...")
API_URL = "https://jsonplaceholder.typicode.com/users"  # Sample API  
df_api = ingestion.fetch_from_api(API_URL)
if df_api is not None:
    print("\n Cleaning API Data...")
    df_api = df_api.head(30)  # Limit to 30 records for testing

    if "body" in df_api.columns:
        df_api["body"] = df_api["body"].apply(lambda x: x[:100]+ "..." if isinstance(x, str) else x)  # Truncate long text for testing
    
    df_api = cleaner.clean_data(df_api)
    df_api = ai_agent.process_data(df_api)
    print("✅ API Cleaned Data:\n", df_api.head())
    print("\n🎉 Pipeline Complete!")