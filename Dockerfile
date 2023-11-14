#Base Image to use
FROM python:3.11-slim

#Change Working Directory to app directory
WORKDIR /app

#Copy Requirements.txt file into app directory
COPY . .

#install all requirements in requirements.txt
RUN pip install -r /app/requirements.txt

#Expose port 8080
EXPOSE 8080

#Run the application on port 8080
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]