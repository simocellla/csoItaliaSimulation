FROM python:3.7

COPY . /my-flask-app
WORKDIR /my-flask-app
#COPY server.py ./
RUN pip install -r requirements.txt
# RUN pip install gunicorn
# ENV FLASK_APP /api/server.py

#CMD gunicorn --bind 0.0.0.0:5000 wsgi:api

#CMD ["python","./app.py"]
#EXPOSE 8813
CMD ["flask", "run", "--host", "127.0.0.1", "--port", "8813"]
