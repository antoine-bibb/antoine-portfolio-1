from fastapi import FastAPI

from app.api.routes import router as clip_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(clip_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
