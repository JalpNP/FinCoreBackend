from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from database import users_collection, companies_collection, financial_years_collection
from schemas import UserCreate, UserLogin, FinancialYearCreate
import hashlib
import os
import shutil
from uuid import uuid4

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

auth_router = APIRouter()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@auth_router.post("/register")
async def register_user(user: UserCreate):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    new_user = {
        "firstName": user.firstName,
        "lastName": user.lastName,
        "email": user.email,
        "password": hashed_password,
    }
    users_collection.insert_one(new_user)
    return {"message": "Registration successful"}

@auth_router.post("/login")
async def login_user(user: UserLogin):
    stored_user = users_collection.find_one({"email": user.email})
    if not stored_user or stored_user["password"] != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful", "email": user.email}

@auth_router.get("/companies")
async def get_companies():
    companies = list(companies_collection.find())
    for company in companies:
        company["_id"] = str(company["_id"])
    return companies

@auth_router.post("/companies")
async def add_company(
    name: str = Form(...), coa_type: str = Form(...), logo: UploadFile = File(...),
):
    existing_company = companies_collection.find_one({"name": name})
    if existing_company:
        raise HTTPException(status_code=400, detail="Company name already exists")

    file_extension = logo.filename.split(".")[-1]
    filename = f"{uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(logo.file, buffer)

    new_company = {
        "name": name,
        "coa_type": coa_type,
        "logo": filename,
    }
    inserted_company = companies_collection.insert_one(new_company)
    new_company["_id"] = str(inserted_company.inserted_id)

    return new_company

@auth_router.post("/financial-years")
async def add_financial_year(financial_year: FinancialYearCreate):
    company = companies_collection.find_one({"name": financial_year.company_name})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    financial_years = company.get("financial_years", [])
    year_no = len(financial_years) + 1

    new_year = {
        "year_no": year_no,
        "start_of_year": financial_year.start_of_year.isoformat(),
        "end_of_year": financial_year.end_of_year.isoformat(),
        "fy": financial_year.fy,
    }

    companies_collection.update_one(
        {"name": financial_year.company_name},
        {"$push": {"financial_years": new_year}}
    )

    return {"message": "Financial year added successfully"}

@auth_router.get("/financial-years/{company_name}")
async def get_financial_years(company_name: str):
    financial_years = list(financial_years_collection.find({"company_name": company_name}))
    for year in financial_years:
        year["_id"] = str(year["_id"])
    return financial_years
