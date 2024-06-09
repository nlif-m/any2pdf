FROM docker.io/python:3.12-slim

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache  pip3 install -r requirements.txt

COPY . .
CMD ["python3", "main.py"]
