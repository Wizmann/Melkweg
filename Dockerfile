# Melkweg runs on Python 2
FROM python:2

# Create app directory
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

# Bundle app source
COPY . /usr/src/app
RUN pip install -r requirements.txt

# Expose port
EXPOSE 20000

# Start
CMD [ "python", "src/server.py"]
