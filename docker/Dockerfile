FROM python:3.7-stretch

WORKDIR /pandemic

COPY . .

RUN ls
RUN pip install -e /pandemic

ENTRYPOINT python -c "import pandemic; pandemic.run(plot=False)"
