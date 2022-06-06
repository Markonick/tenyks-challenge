FROM python:3.9-slim

EXPOSE 8002

WORKDIR /app
COPY app/ml_extraction /app/ml_extraction
COPY app/shared /app/shared
COPY app/__init__.py /app
# RUN  --mount=type=cache,target=/root/.cache \
#     pip3 install -r shared/requirements.txt

RUN  pip3 install -r shared/requirements.txt
CMD ["uvicorn", "ml_extraction.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]