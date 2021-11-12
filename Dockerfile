FROM python:latest
LABEL Name=spiderdoc Version=0.0.1
WORKDIR /home/spiderdoc/spiderdoc
RUN python3 -m venv /venv

# Install dependencies:
COPY requirements.txt .
RUN /venv/bin/pip install -r requirements.txt

# Run the application:
COPY printAmnt.py .
CMD . /venv/bin/activate && exec python printAmnt.py
