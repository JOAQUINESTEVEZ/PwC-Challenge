from pydantic import BaseModel, EmailStr, Field

class SignupRequest(BaseModel):
    # User data
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    # Client data
    company_name: str = Field(..., max_length=100)
    industry: str = Field(..., max_length=50)
    contact_email: EmailStr
    contact_phone: str = Field(..., max_length=50)
    address: str