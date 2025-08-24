"""API and web service patterns."""

from typing import List
from ..db_manager import Pattern


def get_api_patterns() -> List[Pattern]:
    """Get API-related patterns."""
    return [
        Pattern(
            name="fastapi_crud_endpoints",
            language="python",
            pattern_type="api",
            code_snippet="""
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
""",
            usage_context="FastAPI CRUD endpoint patterns",
            dependencies=["fastapi", "sqlalchemy"],
            success_count=35
        ),
        Pattern(
            name="api_middleware_pattern",
            language="python",
            pattern_type="api",
            code_snippet="""
from fastapi import Request, Response
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
""",
            usage_context="FastAPI middleware for cross-cutting concerns",
            dependencies=["fastapi"],
            success_count=28
        ),
        Pattern(
            name="jwt_authentication",
            language="python",
            pattern_type="api",
            code_snippet="""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
def protected_route(current_user: str = Depends(verify_token)):
    return {"message": f"Hello {current_user}"}
""",
            usage_context="JWT authentication for API endpoints",
            dependencies=["fastapi", "python-jose"],
            success_count=32
        ),
        Pattern(
            name="api_error_handling",
            language="python",
            pattern_type="api",
            code_snippet="""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class APIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "details": exc.errors()}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
""",
            usage_context="Comprehensive API error handling",
            dependencies=["fastapi"],
            success_count=30
        ),
        Pattern(
            name="rate_limiting",
            language="python",
            pattern_type="api",
            code_snippet="""
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside the window
        client_requests[:] = [req_time for req_time in client_requests 
                             if now - req_time < self.window_seconds]
        
        if len(client_requests) >= self.max_requests:
            return False
        
        client_requests.append(now)
        return True

def rate_limit_dependency(request: Request):
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
""",
            usage_context="Rate limiting for API protection",
            dependencies=["fastapi"],
            success_count=26
        )
    ]