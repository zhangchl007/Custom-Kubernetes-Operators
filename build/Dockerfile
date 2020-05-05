FROM python:3
RUN pip install gunicorn flask
ADD mainapp.py wsgi.py /app/
ADD config /config
EXPOSE 5000
WORKDIR /app
CMD [ "gunicorn","--bind","0.0.0.0:5000","wsgi:app" ]
