FROM python:3
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT DEV

#ENV SECRET_KEYe 1$qpv*d%uox8xe!as6r0#3s@kz1)e&tpb5a@@@)y#dr(5_**t
#ENV DB_NAME cic_dashboard
#ENV DB_USER dashboard
#ENV DB_HOST cic-dashboard-prod-db.chsn5n41tx4z.eu-central-1.rds.amazonaws.com
#ENV DB_PASS q!DtaGq8BPIhu

ENV DB_CACHE redis://cic-prod-redis.13yrwl.ng.0001.euc1.cache.amazonaws.com:6379/1

RUN mkdir /code
RUN mkdir /code/static

WORKDIR /code

RUN pip install uwsgi

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

RUN python3 manage.py collectstatic

EXPOSE 8080

CMD ["uwsgi", "--ini", "/code/cic-dashboard.ini"]