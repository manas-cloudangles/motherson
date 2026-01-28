# uvicorn imported in main block
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.config.config import LOG_LEVEL

app = FastAPI(
    title="Angular Page Generator API",
    description="API for generating Angular components with LLM assistance",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("ANGULAR PAGE GENERATOR API SERVER (FastAPI)")
    print("="*60)
    print("\nServer starting on http://localhost:5000")
    
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level=LOG_LEVEL.lower())
