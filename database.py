from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database("fincore")
users_collection = db.get_collection("register")
companies_collection = db.get_collection("companies")
financial_years_collection = db.get_collection("financial_years")