from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.Webhandler import auth_routes
from app.core.db import init_db
from app.exception.exceptions import http_exception_handler, validation_exception_handler
from app.routers import employees, leaves
from app.Webhandler.protect_routes import router as protected_router

app = FastAPI(title="Leave Management API", version="0.1.0")

# ----------------- Initialize DB -----------------
init_db()

# ----------------- Exception Handlers -----------------
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# ----------------- CORS Middleware -----------------
origins = [
    "http://localhost:3000",  # React frontend
    # Add production frontend URL here when deployed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Include Routers -----------------
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(protected_router)
app.include_router(employees.router, prefix="/employees", tags=["Employees"])
app.include_router(leaves.router, prefix="/leaves", tags=["Leaves"])

# ----------------- Root -----------------
@app.get("/")
def root():
    return {"message": "Hello World"}
