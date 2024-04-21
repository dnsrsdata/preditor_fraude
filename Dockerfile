FROM python:3.10.12-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y libgomp1

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8080

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8080"]