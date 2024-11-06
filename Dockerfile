<<<<<<< HEAD
FROM python:3.12.3-alpine
WORKDIR /app
COPY requirements.txt ./
# COPY config*.json ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
=======
FROM python:3.12.4-alpine
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
>>>>>>> origin/main
CMD [ "python", "app.py" ]