FROM python:3.8.12

RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
    sed -i 's http://.*.debian.org http://mirrors.aliyun.com g' /etc/apt/sources.list

RUN mkdir /code \
&&apt-get update \
&&apt-get -y install freetds-dev \
&&apt-get -y install unixodbc-dev

COPY email_name_dict.py /code
COPY gitlab_commit_stats.py /code
COPY run.sh /code
COPY requirements.txt /code

RUN pip install -r /code/requirements.txt -i https://pypi.douban.com/simple

WORKDIR /code


CMD ["/bin/bash","run.sh"]
