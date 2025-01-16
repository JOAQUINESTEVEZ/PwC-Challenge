from fastapi import FastAPI
from sqlalchemy import text
from app.db import engine
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from app.config import settings
from app.routes import auth_route

# Initialize the FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_route.router, prefix="/auth", tags=["Authentication"])

# Healthcheck and version endpoints
@app.get("/healthcheck", tags=["Healthcheck"])
def healthcheck():
    return {"status": "ok"}

@app.get("/version", tags=["Version"])
def version():
    return {"version": "1.0.0"}

# Error handler for Problem Details
@app.exception_handler(Exception)
def problem_details_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc),
            "instance": str(request.url)
        }
    )