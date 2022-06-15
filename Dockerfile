FROM osgeo/gdal:alpine-small-latest

RUN apk add --no-cache --upgrade bash

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python

RUN mkdir /src

WORKDIR /src

RUN pip3 install rasterio geojson

COPY script.py .

CMD python script.py
