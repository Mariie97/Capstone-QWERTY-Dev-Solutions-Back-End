FROM  python:3.8
WORKDIR /api
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
# ENTRYPOINT is supposed to run flask app
