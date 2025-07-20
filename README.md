# GABM Interviewer Platform

A Django-based interview platform with audio recording capabilities, real-time transcription, and AI-powered interview analysis.

## Features

- 🎙️ Audio recording and transcription
- 🤖 AI-powered interview analysis using OpenAI
- 👥 User authentication with Google OAuth
- 📊 Interview analytics and reporting
- 🐳 Docker containerization
- 🗄️ PostgreSQL database
- 🔄 Real-time interview progress tracking

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd gabm_interviewer_platform
```

### 2. Environment Setup

Copy the environment template and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database Configuration
DATABASE_URL=postgresql://postgres:your-postgres-password@db:5432/gabm_interviewer
POSTGRES_DB=gabm_interviewer
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-postgres-password

# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key

# Optional: Google OAuth (if using social auth)
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
```

### 3. Run with Docker

```bash
# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec web python manage.py migrate

# Create a superuser (optional)
docker-compose exec web python manage.py createsuperuser

# Collect static files (should be automatic, but if needed)
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Access the Application

- **Web Interface**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Database**: localhost:5432 (credentials from .env)

## Development Setup

### Local Development (without Docker)

1. **Install Python 3.11.5** and create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Setup local PostgreSQL**:

```bash
# macOS with Homebrew
brew install postgresql
brew services start postgresql
createdb gabm_interviewer

# Update .env to use local database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/gabm_interviewer
```

4. **Run migrations and start server**:

```bash
python manage.py migrate
python manage.py runserver
```

## Project Structure

```
gabm_interviewer_platform/
├── gabm_infra/                 # Main Django project
│   ├── settings/               # Settings modules
│   │   ├── base.py            # Base settings
│   │   ├── production.py      # Production settings
│   │   └── __init__.py        # Settings loader
│   ├── urls.py                # URL configuration
│   └── wsgi.py                # WSGI application
├── pages/                      # Main application
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── forms.py               # Django forms
│   └── ...
├── interviewer_agent/          # AI interview logic
│   ├── agent_modules/         # Interview modules
│   ├── prompt_template/       # AI prompts
│   └── interviewer_utils/     # Utilities
├── static_dirs/               # Static source files
├── static_root/               # Collected static files
├── media_root/                # User uploads
├── templates/                 # HTML templates
├── docker-compose.yml         # Docker services
├── Dockerfile                 # Web app container
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | Yes |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | Yes |
| `DATABASE_URL` | PostgreSQL connection URL | Yes |
| `OPENAI_API_KEY` | OpenAI API key for AI features | Yes |
| `GOOGLE_OAUTH2_CLIENT_ID` | Google OAuth client ID | No |
| `GOOGLE_OAUTH2_CLIENT_SECRET` | Google OAuth client secret | No |

### Database Settings

The application uses PostgreSQL with the following default configuration:
- Database: `gabm_interviewer`
- User: `postgres`
- Port: `5432`

## Deployment

### Docker Deployment

The application is containerized and ready for deployment on any Docker-compatible platform:

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d
```

### Coolify Deployment

1. Upload your repository to Git
2. In Coolify, create a new service using "Docker Compose"
3. Point to your repository
4. Set environment variables in Coolify dashboard
5. Deploy

### Manual Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Install Python dependencies
4. Run migrations
5. Collect static files
6. Configure web server (nginx/Apache)
7. Use Gunicorn as WSGI server

## API Endpoints

- `/` - Home page
- `/admin/` - Django admin panel
- `/accounts/` - Authentication (allauth)
- `/interview/<script_v>/` - Interview interface
- `/summary` - Interview summaries
- `/download_p_data/<username>/<script>/` - Download participant data

## Troubleshooting

### Common Issues

1. **Static files not loading**
   - Ensure WhiteNoise is installed: `pip install whitenoise`
   - Run: `docker-compose exec web python manage.py collectstatic`

2. **Database connection errors**
   - Check PostgreSQL is running: `docker-compose ps`
   - Verify DATABASE_URL in .env

3. **OpenAI API errors**
   - Verify OPENAI_API_KEY is set correctly
   - Check API quota and billing

4. **Audio recording issues**
   - Ensure HTTPS for production (required for audio)
   - Check browser permissions

### Logs

```bash
# View application logs
docker-compose logs web

# View database logs
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review application logs for error details