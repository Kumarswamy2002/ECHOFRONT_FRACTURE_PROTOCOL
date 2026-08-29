from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import init_db, AsyncSessionLocal
from backend.app.services.seed_data_service import seed_master_game_data
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.player import router as player_router
from backend.app.api.v1.inventory import router as inventory_router
from backend.app.api.v1.store import router as store_router
from backend.app.api.v1.matchmaking import router as matchmaking_router
from backend.app.api.v1.game_server import router as gameserver_router
from backend.app.api.v1.admin import router as admin_router
from backend.app.api.v1.battle_pass import router as battle_pass_router
from backend.app.websockets.routes import router as ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & Seed Master Assets
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_master_game_data(session)
    print(">> [ECHOFRONT BACKEND]: Database initialized & master operatives seeded.")
    yield
    # Shutdown logic
    print(">> [ECHOFRONT BACKEND]: Server shutting down gracefully.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Authoritative Enterprise Backend for ECHOFRONT: Fracture Protocol",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permissive in local dev for game client and admin portal
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(player_router, prefix=settings.API_V1_STR)
app.include_router(inventory_router, prefix=settings.API_V1_STR)
app.include_router(store_router, prefix=settings.API_V1_STR)
app.include_router(matchmaking_router, prefix=settings.API_V1_STR)
app.include_router(gameserver_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(battle_pass_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
