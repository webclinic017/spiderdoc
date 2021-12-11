FROM python:latest
LABEL Name=SMA Version=1.0.0
WORKDIR /
# Install dependencies:
COPY ./requierments/min_max_req.txt .
RUN pip install -r min_max_req.txt
# Run the application:
COPY ./strategy/local_min_max.py /
COPY /input /input
ENTRYPOINT ["python","./local_min_max.py"]