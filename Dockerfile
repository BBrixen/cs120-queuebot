FROM python:3.8-buster

ENV QUEUE_USE_ENV=1

WORKDIR /app/
COPY requirements-prod.txt /app/
RUN pip install --no-cache-dir -r requirements-prod.txt
COPY queuebot.py constants.py tasks_and_events.py /app/
COPY test/utils.py /app/test/

ENTRYPOINT [ "python", "queuebot.py" ]