from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for Pydantic validation errors"""
    errors = []
    
    for error in exc.errors():
        field_name = error['loc'][-1] if error['loc'] else 'unknown'
        message = error['msg']
        if message.startswith('Value error, '):
            message = message[13:]
        
        errors.append({field_name: message})
    
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )

# Add other exception handlers here
async def http_exception_handler(request: Request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )