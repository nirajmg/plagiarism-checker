FROM  python:3.8-alpine3.17

COPY ./requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "-m", "run", "subscriber.py"]