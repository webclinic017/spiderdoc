FROM python:latest
LABEL Name=SMA Version=1.0.0
WORKDIR /
# Install dependencies:
COPY ./requierments/SMA_req.txt .
RUN pip install -r SMA_req.txt
# Run the application:
COPY ./strategy/SMA.py /
COPY /input /input
ENTRYPOINT ["python","./SMA.py"]
