FROM  python:3.8

COPY ./requirements.txt ./requirements.txt
# RUN apk add --no-cache bash pkgconfig  git gcc openldap libcurl python2-dev gpgme-dev libc-dev 
RUN python -m pip install --upgrade pip  && pip3 install --upgrade setuptools && pip install -r requirements.txt
COPY . .

CMD ["python", "process.py"]