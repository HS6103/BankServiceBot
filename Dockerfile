#Create a ubuntu base image with python 3 installed.
FROM python:3.11-slim

#Set the working directory
WORKDIR /esunNonOfficialBot

#copy all the files
COPY . .

#Install the dependencies
RUN pip3 install -r requirements.txt

#Expose the required port
EXPOSE 5000

#Run the command
CMD gunicorn app:app