#ENV GITHUB_SECRET="your secret"
FROM python:alpine
COPY ./ /app
RUN apk add --no-cache git openssh && \
    pip install -r /app/requirements.txt
EXPOSE 5000
CMD ["python", "/app/github-webhook.py"]
