from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routes import router
from app.utils.logger import app_logger
from app.models.model_loader import load_model



# ------------------------------------------------
# Lifespan (Modern FastAPI Startup/Shutdown)
# ------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup logic
    try:
        model, model_id = load_model()
        app.state.model = model
        app.state.model_id = model_id

        app_logger.info(f"Model loaded successfully: {model_id}")

    except Exception as e:
        app_logger.error(f"Model loading failed: {str(e)}")
        app.state.model = None
        app.state.model_id = None

    app_logger.info("RISKSAARTHI API Started")

    yield

    # Shutdown logic (optional)
    app_logger.info("RISKSAARTHI API Shutting Down")


# ------------------------------------------------
# FastAPI App
# ------------------------------------------------

app = FastAPI(
    title="RISKSAARTHI – AI Loan Risk Prediction System",
    version="1.0.0",
    description="AI-powered system to predict loan default risk using ML models",
    lifespan=lifespan
)


# ------------------------------------------------
# Root Endpoint
# ------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "RISKSAARTHI API Running Successfully"
    }


# ------------------------------------------------
# Include Routes
# ------------------------------------------------

app.include_router(router, prefix="/api")



@app.on_event("startup")
def load():
    model, model_id = load_model()

    app.state.model = model
    app.state.model_id = model_id
