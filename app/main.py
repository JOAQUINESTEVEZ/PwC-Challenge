from fastapi import FastAPI
from sqlalchemy import text
from app.db import engine

# Initialize the FastAPI app
app = FastAPI()

# Basic endpoint to check if the app is running
@app.get("/")
def read_root():
    return {"message": "FastAPI is working!"}

# Optional: Test route to confirm DB connection
@app.get("/test-db")
def test_db_connection():
    try:
        with engine.connect() as connection:
            # Execute the query and fetch all results
            result = connection.execute(text("SELECT * FROM roles"))
            # Convert the result to a list of dictionaries
            roles = [dict(row._mapping) for row in result]
            
            return {
                "db_connection": "success",
                "roles": roles
            }
    except Exception as e:
        return {
            "db_connection": "failure",
            "error": str(e)
        }