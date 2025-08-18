# main.py
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.Webhandler import auth_routes
from app.core.db import init_db
from app.exception.exceptions import http_exception_handler, validation_exception_handler
from app.routers import employees, leaves
from app.Webhandler.protect_routes import router as protected_router

app = FastAPI(title="Leave Management API", version="0.1.0")

# init tables
init_db()
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)



# app.include_router(auth_routes.router)
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(protected_router)
# Routers
app.include_router(employees.router, prefix="/employees", tags=["Employees"])
app.include_router(leaves.router, prefix="/leaves", tags=["Leaves"])

@app.get("/")
def root():
    return {"message": "Hello World"}
