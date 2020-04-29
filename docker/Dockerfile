FROM python:3.7-stretch

LABEL git="https://github.com/xtellurian/pandemic/"
LABEL author="Rian Finnegan"

WORKDIR /pandemic
COPY . .
# install the local pandemic from this repository
RUN pip install -e /pandemic

ENTRYPOINT python -c "import pandemic; pandemic.run(plot=False)"
