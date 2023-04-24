FROM python:3.10.2

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 443

CMD ["gunicorn", "--bind", "0.0.0.0:443", "app:app"]