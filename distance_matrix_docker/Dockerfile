FROM python:3.6-alpine

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENV IN_DOCKER 1
ENV PYTHONPATH "${PYTHONPATH}:/app"
CMD ["python", "/app/scripts/get_matrix.py"]


