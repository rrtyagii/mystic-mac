FROM amazonlinux:2

RUN yum -y groupinstall development && \
    yum -y install openssl-devel bzip2-devel libffi-devel wget zip && \
    yum clean all

RUN wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz && \
    tar xzf Python-3.9.16.tgz && \
    cd Python-3.9.16 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.9.16.tgz Python-3.9.16

COPY . /app

WORKDIR /app

RUN python3.9 -m pip install --upgrade pip && \
    python3.9 -m pip install -r requirements.txt -t package

RUN cp lambda_function.py package/ && \
    mkdir -p package && \
    cd package && \
    zip -r ../deployment_package.zip . && \
    echo "Deployment package created successfully."
