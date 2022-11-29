FROM python:3

WORKDIR /WebUI

# Install dependencies for frontend and backend
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the files
COPY webUI.py webUI.py

# Not needed I guess
ENTRYPOINT []

# Run the code
CMD ["python", "-u", "rest-server.py"]
