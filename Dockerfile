FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SSH_PRIVATE_KEY=${SSH_PRIVATE_KEY}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8971", "--reload"]