# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set timezone
#RUN apt-get update && apt-get install -y libpq-dev gcc tzdata && \
 #   ln -sf /usr/share/zoneinfo/Asia/Tbilisi /etc/localtime && \
 #   echo "Asia/Tbilisi" > /etc/timezone

 RUN apt-get update && apt-get install -y libpq-dev gcc netcat-openbsd tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Tbilisi /etc/localtime && \
    echo "Asia/Tbilisi" > /etc/timezone


# Add system dependencies for PostgreSQL
# RUN apt-get update && apt-get install -y libpq-dev gcc

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# CMD ["python", "backend/app.py"]

# ENV FLASK_APP=app.py


ENV FLASK_APP=backend.app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
