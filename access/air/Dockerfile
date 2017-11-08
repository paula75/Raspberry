FROM resin/rpi-raspbian:jessie

MAINTAINER Felipe Lalanne <felipe@lalanne.cl>

#RUN echo "deb http://archive.raspbian.org/raspbian jessie main" > /etc/apt/sources.list
#RUN apt-get update && apt-get -q -y install \
#        wireless-tools \
#        wpasupplicant \
#        python \
#        python-pip

ADD . /air
WORKDIR /air
RUN pip install -r requirements.txt

EXPOSE 5000

ENV FLASK_DEBUG=0
ENV FLASK_APP=main.py
CMD [ "flask", "run", "--host=0.0.0.0" ]
