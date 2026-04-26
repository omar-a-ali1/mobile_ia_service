FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    && rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt /app/

ENV DLIB_COMPILATION_THREADS=4

RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "main.py"]