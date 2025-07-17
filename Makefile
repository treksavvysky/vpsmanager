.PHONY: all install run

# Default target to install dependencies and run the server
all: install run

# Target to install dependencies from requirements.txt without redundancy
install:
	@echo "Installing dependencies..."
	@python /app/add_packages.py `cat /app/requirements.txt`

# Target to run the uvicorn server
run:
	@echo "Running uvicorn server..."
	@uvicorn main:app --host 0.0.0.0 --port 8971 --reload
