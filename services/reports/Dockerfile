# FROM google/cloud-sdk:alpine
FROM  python:3.8-alpine3.17

COPY ./requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
RUN pip install google-cloud-pubsub

COPY . .

CMD ["python", "subscriber.py"]