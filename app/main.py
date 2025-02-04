from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from app.config import settings
from app.container import Container
from app.routes import auth_route, client_route, financial_transaction_route, invoice_route
from app.middleware.logging_middleware import LoggingMiddleware

# Create and configure the container
container = Container()
container.config.from_dict({
    "database_url": settings.database_url,
    "secret_key": settings.secret_key,
    "algorithm": settings.algorithm,
    "access_token_expire_minutes": settings.access_token_expire_minutes,
})

# Initialize the FastAPI app
app = FastAPI(
    title="Financial Management API",
    description="API for managing clients, invoices, and financial transactions"
)

# Add logging middleware FIRST (to catch all requests)
app.add_middleware(LoggingMiddleware)

# Store container in app instance
app.container = container

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
app.include_router(client_route.router, prefix="/clients", tags=["Clients"])
app.include_router(financial_transaction_route.router,prefix="/finance/transactions",tags=["Finance"])
app.include_router(invoice_route.router, prefix="/invoices", tags=["Invoices"])

# Healthcheck and version endpoints
@app.get("/healthcheck", tags=["Healthcheck"])
def healthcheck():
    return {"status": "ok"}

@app.get("/version", tags=["Version"])
def version():
    return {
        "version": "2.0.0",
        "release_date": "2025-01-29",
        "changelog": "Added container for DI and IoC"
    }

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

