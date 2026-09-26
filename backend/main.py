from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.customers import router as customers_router


app = FastAPI(
    title="UniBank Customer 360 API",
    description="API for Customer 360 data",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "UniBank Customer 360 API",
    }