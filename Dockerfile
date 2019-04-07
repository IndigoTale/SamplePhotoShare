FROM python:3.6
ARG project_dir=/flask/
ADD requirements.txt $project_dir 
ADD app $project_dir
WORKDIR $project_dir
RUN pip install -r requirements.txt
RUN python3 app/app.py