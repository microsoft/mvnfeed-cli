FROM --platform=arm64 python:3-bookworm

RUN mkdir /opt/app 
WORKDIR /opt/app

# Have to use older pyyaml than the container provides
# https://github.com/yaml/pyyaml/issues/601#issuecomment-1693730229
# it's even more fun, because python dependencies are a nightmare.
RUN pip install "Cython<3.0" pyyaml==5.4.1 --no-build-isolation \
    && pip install requests

COPY . /opt/app
RUN python3 scripts/dev_setup.py \
  && mkdir /srv/mvnfeed_stage \
  && mvnfeed -h


# configuration file is at ~/.mvnfeed/mvnfeed.ini

ENTRYPOINT ["/usr/local/bin/mvnfeed"]