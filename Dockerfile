FROM python:3

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/threatcode/sqliv.git
WORKDIR /sqliv
RUN pip install -r requirements.txt && python setup.py -i

ENTRYPOINT ["python","sqliv.py"]
CMD ["--help"]
