FROM python:3.14.0rc3-alpine

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]