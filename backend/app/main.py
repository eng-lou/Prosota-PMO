from fastapi import FastAPI

from app.api.activities import router as activities_router
from app.api.cost_elements import router as cost_elements_router
from app.api.icd_items import router as icd_items_router
from app.api.record_links import router as record_links_router
from app.api.risks import router as risks_router

app = FastAPI(title="ProsotaPMO API", version="0.1.0")

app.include_router(activities_router, prefix="/api/v1")
app.include_router(risks_router, prefix="/api/v1")
app.include_router(record_links_router, prefix="/api/v1")
app.include_router(cost_elements_router, prefix="/api/v1")
app.include_router(icd_items_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
