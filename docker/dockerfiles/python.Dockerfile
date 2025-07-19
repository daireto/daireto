FROM python:3.10.14-slim

ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Use it in the code to check if program is running in a docker container
ENV RUNNING_IN_A_DOCKER_CONTAINER=yes

RUN rm /etc/localtime
RUN ln -s /usr/share/zoneinfo/America/Bogota /etc/localtime

RUN apt update && apt install --yes \
    curl inetutils-ping wget telnet vim

# To avoid SSL verification
# RUN apt update && apt install --yes --no-install-recommends \
#    curl inetutils-ping wget telnet vim

WORKDIR /usr/src/app
COPY . .

RUN pip install -r requirements.txt
# To avoid SSL verification
# RUN pip install --no-cache-dir --disable-pip-version-check --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

CMD [ "python", "main.py"]
