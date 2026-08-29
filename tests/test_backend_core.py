import os
import sys
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.app.core.database import init_db, AsyncSessionLocal
from backend.app.services.seed_data_service import seed_master_game_data

@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_master_game_data(session)
    yield

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_register_and_login_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        suffix = uuid.uuid4().hex[:8]
        test_email = f"operative_{suffix}@echofront.gg"
        test_username = f"Apex_{suffix}"
        test_password = "StrongPassword2026!"

        # 1. Register unique player
        reg_payload = {
            "email": test_email,
            "username": test_username,
            "password": test_password,
            "display_name": f"Apex {suffix}"
        }
        reg_res = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
        data = reg_res.json()
        assert "access_token" in data
        assert data["username"] == test_username

        # 2. Login
        login_payload = {
            "username": test_username,
            "password": test_password
        }
        login_res = await ac.post("/api/v1/auth/login", json=login_payload)
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Get Profile
        prof_res = await ac.get("/api/v1/player", headers=headers)
        assert prof_res.status_code == 200
        prof_data = prof_res.json()
        assert prof_data["credits"] == 5000
        assert prof_data["fracture_shards"] == 200

        # 4. List Operatives
        ops_res = await ac.get("/api/v1/player/operatives", headers=headers)
        assert ops_res.status_code == 200
        ops = ops_res.json()
        assert len(ops) >= 12

        # 5. Join Matchmaking Queue
        mm_payload = {
            "game_mode": "Fracture",
            "region": "us-east",
            "operative_code": "OP_APEX"
        }
        mm_res = await ac.post("/api/v1/matchmaking/join", json=mm_payload, headers=headers)
        assert mm_res.status_code == 200
        ticket_id = mm_res.json()["ticket_id"]
        assert "TICKET_" in ticket_id
