FROM ubuntu:19.10

LABEL maintainer="Jan \"yaqwsx\" Mrázek" \
      description="Container for running PCB presentation applications"

ENV DISPLAY=:0

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        kicad \
        nodejs npm libxtst6 libnss3-tools libgbm-dev libasound-dev xvfb \
        make pandoc \
        python3 python3-pip python3-wheel python3-setuptools python3-psutil

RUN pip3 install plotly click pandas pybars3 kikit pcbdraw requests
RUN npm install -g electron orca --unsafe-perm=true --allow-root

CMD ["bash"]
