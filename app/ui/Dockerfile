FROM python:3.9-slim

EXPOSE 5000

WORKDIR /setup
COPY /setup /setup

RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

RUN pip install -r requirements.txt

CMD python main.py