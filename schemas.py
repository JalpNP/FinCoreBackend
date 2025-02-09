from pydantic import BaseModel, EmailStr
from datetime import date

class UserCreate(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CompanyCreate(BaseModel):
    name: str
    coa_type: str
    logo: str

class FinancialYearCreate(BaseModel):
    company_name: str
    start_of_year: date
    end_of_year: date
    year_no: int
    fy: str

