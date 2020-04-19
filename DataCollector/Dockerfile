FROM ubuntu:latest

RUN apt update && apt upgrade -y

RUN apt install -y \
    python3-pip \
    python3-dev \
    wget

RUN cd /usr/local/bin && ln -s /usr/bin/python3 python

RUN pip3 install --upgrade pip

RUN mkdir /src && mkdir /src/DataCollector && cd /src/DataCollector

ADD requirements.txt /src/DataCollector/requirements.txt

RUN cd /src/DataCollector && pip3 install -r requirements.txt

RUN wget http://step.esa.int/thirdparties/sen2cor/2.8.0/Sen2Cor-02.08.00-Linux64.run 

RUN bash Sen2Cor-02.08.00-Linux64.run --target /src/sen2cor

RUN ln -s /src/sen2cor/bin/L2A_Process /bin/L2A_Process

     
