FROM python:latest
RUN pip install numpy matplotlib scipy plotly influxdb flask pandas
COPY . .
CMD python dashboard.py influxdb