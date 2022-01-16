FROM python:latest
LABEL Name=ROC Version=1.0.0
WORKDIR /
# Install dependencies:
COPY ./requierments/min_max_req.txt .
RUN pip install -r strategy_req.txt
# Run the application:
COPY ./strategy/strategy.py /
COPY /input /input
ENTRYPOINT ["python","./strategy.py"]