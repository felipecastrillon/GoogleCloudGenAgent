FROM python:3.10-slim
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV PORT 8080 
ENV GOOGLE_CLOUD_PROJECT <PROJECT_ID> 
COPY requirements.txt /$APP_HOME/
COPY docs/ /$APP_HOME/
COPY src/ /$APP_HOME/
WORKDIR $APP_HOME
RUN ls -la $APP_HOME
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
