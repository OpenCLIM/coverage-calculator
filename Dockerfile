FROM python:3.8

RUN apt-get -y update

RUN apt-get -y install

RUN apt-get install gdal-bin -y

RUN pip3 install rasterio geojson

RUN mkdir /src

WORKDIR /src

COPY script.py .

CMD python script.py
