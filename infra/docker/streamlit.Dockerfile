# SolarOps AI — Frontend (Streamlit) image
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8501

ENV BACKEND_URL=http://backend:8000

CMD ["python", "-m", "streamlit", "run", "streamlit_app/app.py", \
     "--server.port", "8501", "--server.address", "0.0.0.0"]
