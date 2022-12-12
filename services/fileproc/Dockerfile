FROM  python:3.8-alpine3.17

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY file-proc-service.py file-proc-service.py

ENTRYPOINT []

CMD ["python", "-u", "file-proc-service.py"]
