
FROM python:3.8-alpine
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
ENTRYPOINT [ "python" ]
# CMD [ "flask", "run","--host","0.0.0.0","--port","8080"]
CMD ["server.py"]
