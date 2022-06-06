FROM python:3.9-slim

EXPOSE 8001

WORKDIR /app
COPY app/ui /app/ui
COPY app/shared /app/shared
COPY app/__init__.py /app
# RUN  --mount=type=cache,target=/root/.cache \
#     pip3 install -r shared/requirements.txt

RUN  pip3 install -r shared/requirements.txt
CMD ["uvicorn", "ui.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]