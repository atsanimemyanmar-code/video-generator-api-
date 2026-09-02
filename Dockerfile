FROM python:3.10-slim
RUN apt-get update && apt-get install -y ffmpeg imagemagick
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "unlimited_video_engine:app", "--host", "0.0.0.0", "--port", "8000"]
