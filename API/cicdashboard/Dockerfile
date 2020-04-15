FROM python:3.7.6
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT ${env}

ENV SECRET_KEY 1$qpv*d%uox8xe!as6r0#3s@kz1)e&tpb5a@@@)y#dr(5_**t

ARG DB_NAME
ARG DB_USER
ARG DB_HOST
ARG DB_PASS

ENV DB_NAME ${DB_NAME}
ENV DB_USER ${DB_USER}
ENV DB_HOST ${DB_HOST}
ENV DB_PASS ${DB_PASS}

RUN mkdir /code
RUN mkdir /code/static

WORKDIR /code
RUN pip install uwsgi
RUN pip install web3

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

RUN python3 manage.py collectstatic

EXPOSE 8080

CMD ["uwsgi", "--ini", "/code/cic-dashboard.ini"]
