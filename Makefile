# AI Events Intelligence Pipeline - Makefile

.PHONY: help install run-api run-frontend run-pipeline run-all test clean

# Default target: show help
help:
	@echo "Available commands:"
	@echo "  make install       - Install Python dependencies"
	@echo "  make run-api       - Start the FastAPI backend server"
	@echo "  make run-frontend  - Start the frontend HTTP server"
	@echo "  make run-pipeline  - Run the full data pipeline (Discovery -> Notifier)"
	@echo "  make run-all       - Start both API and Frontend (requires two terminals, see help)"
	@echo "  make test          - Run unit tests"
	@echo "  make clean         - Remove logs and temporary files"

install:
	pip install -r requirements.txt

run-api:
	cd src && python3 api.py

run-frontend:
	cd frontend && python3 -m http.server 8081

run-pipeline:
	cd src && python3 pipeline.py

# Since API and Frontend need to run concurrently, 
# we suggest running them in separate terminals or using background processes.
run-all:
	@echo "Starting Backend API in background..."
	(cd src && python3 api.py) & \
	echo "Starting Frontend on http://localhost:8081..." && \
	(cd frontend && python3 -m http.server 8081)

test:
	python3 -m unittest discover tests

clean:
	rm -rf logs/*.log
	@echo "Logs cleaned."
