FROM python:3.11

# Root
WORKDIR /app

# Install requirements
RUN apt-get update && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 5000
EXPOSE 5000

# Flask
ENV FLASK_APP=app.py
CMD ["python", "app.py"]
