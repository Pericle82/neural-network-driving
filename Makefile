# Comandi del corso. `make help` per l'elenco.
.PHONY: help install dev server ui notebook test

help:
	@echo "make install         installa dipendenze Python (uv) e UI (npm)"
	@echo "make dev             avvia server di simulazione + UI  →  http://localhost:5173"
	@echo "make server          solo il server Python (porta 8000)"
	@echo "make ui              solo la UI (porta 5173)"
	@echo "make notebook        apre JupyterLab sulla cartella notebooks/"
	@echo "make test            tutti i test"
	@echo "make test STEP=1     solo i test della tappa 1"

install:
	uv sync
	npm --prefix ui install

dev:
	@trap 'kill 0' EXIT; \
	uv run uvicorn server.app:app --reload --port 8000 & \
	npm --prefix ui run dev -- --port 5173 & \
	wait

server:
	uv run uvicorn server.app:app --reload --port 8000

ui:
	npm --prefix ui run dev -- --port 5173

notebook:
	uv run jupyter lab notebooks/

test:
ifdef STEP
	uv run pytest -v tests/test_step$(shell printf '%02d' $(STEP)).py
else
	uv run pytest -v
endif
