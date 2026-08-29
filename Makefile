.PHONY: help install run-backend run-game run-admin test build clean

help:
	@echo "ECHOFRONT: Fracture Protocol - Build Commands"
	@echo "  make install      - Install all backend dependencies"
	@echo "  make run-backend  - Start the FastAPI backend server on port 8000"
	@echo "  make run-game     - Start 3D Game Client HTTP server on port 8080"
	@echo "  make run-admin    - Start Admin Telemetry Portal on port 3000"
	@echo "  make test         - Run automated backend test suite"
	@echo "  make build        - Build all production packages"

install:
	pip install -r backend/requirements.txt

run-backend:
	python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

run-game:
	python -m http.server 8080 --directory game-client

run-admin:
	python -m http.server 3000 --directory admin-portal

test:
	pytest tests/ -v

build:
	python -m py_compile backend/main.py

clean:
	rm -rf __pycache__ .pytest_cache *.db
