import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")  # e.g. postgresql://user:pass@host:5432/db
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX", "juzogo-conversations")
    TENANT_NAME = os.getenv("TENANT_NAME", "JuzoGO")

settings = Settings()
