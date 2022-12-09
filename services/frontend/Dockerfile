FROM  python:3.8-alpine3.17

COPY ./requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

ENV FLASK_APP=app
COPY . /app
EXPOSE 80
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=80"]