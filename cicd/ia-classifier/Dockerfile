FROM oscarvicente/deepscheduler-tensorflow-cuda-base
RUN mkdir /tmp/figs/
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC
RUN apt update
RUN apt install -y graphviz