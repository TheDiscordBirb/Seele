FROM python:3.11.3
WORKDIR /Seele
COPY requirements.txt /Seele/
RUN pip install -r requirements.txt
COPY . /Seele
CMD python main.py