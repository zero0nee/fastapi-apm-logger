FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

#Expose the port of the fastapi app
EXPOSE 80

#Install Filebeat to transfer logs to the elastic container
RUN apt-get update && apt-get install -y make
RUN curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.7.0-linux-x86_64.tar.gz
RUN tar xzvf filebeat-7.7.0-linux-x86_64.tar.gz
COPY ./filebeat/config/filebeat.yml /etc/filebeat/filebeat.yml

#Copy the project to the container
COPY . /app
WORKDIR /app

#Install dependencies 
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --ignore-pipfile

#Run the app
CMD uvicorn api:app --host 0.0.0.0 --port 5057
