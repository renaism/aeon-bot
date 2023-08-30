FROM python:3.10-alpine

WORKDIR /app

COPY . .

RUN pip install --no-deps -r requirements.txt

CMD python main.py