FROM python:3.6.8-stretch
RUN pip install Flask==1.0.2 Flask-Login==0.4.1 boto3==1.9.130 awscli==1.16.140 Flask-Mail==0.9.1 Flask-Cors==3.0.7
RUN adduser flaskapp



