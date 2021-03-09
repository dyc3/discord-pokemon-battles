FROM python:3.7-alpine
ENV FLASK_APP=app.py \
	FLASK_ENV=development \
	FLASK_RUN_HOST=0.0.0.0
VOLUME ["/code"]
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
WORKDIR /code
CMD ["python", "app.py"]
