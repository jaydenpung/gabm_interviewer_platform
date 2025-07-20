FROM python:3.11.5-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libffi-dev \
    libasound2-dev \
    portaudio19-dev \
    python3-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
python manage.py migrate\n\
python manage.py create_default_admin\n\
exec gunicorn --bind 0.0.0.0:8000 gabm_infra.wsgi:application' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]