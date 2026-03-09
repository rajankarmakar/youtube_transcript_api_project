# YouTube Transcript Django REST API

A Django REST API that fetches YouTube video subtitles/transcripts using the [`youtube-transcript-api`](https://pypi.org/project/youtube-transcript-api/) package.

---

## Features

- ✅ Fetch **default transcript** for any YouTube video
- ✅ List **all available languages** for a video
- ✅ Fetch transcript for a **specific language** (with translation fallback)
- ✅ Clean JSON responses with timestamped entries + full text
- ✅ Descriptive error messages (subtitle not found, disabled, video unavailable)
- ✅ Rate limiting (60 req/min per IP)
- ✅ DRF Browsable API for easy browser testing

---

## Project Structure

```
youtube_transcript_api_project/
├── core/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── transcript_app/
│   ├── __init__.py
│   ├── apps.py
│   ├── services.py      ← Business logic / transcript fetching
│   ├── views.py         ← API endpoint handlers
│   └── urls.py          ← URL routing
├── manage.py
├── requirements.txt
└── README.md
```

---

## Setup & Installation

### 1. Clone / navigate to project directory
```bash
cd youtube_transcript_api_project
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Start the development server
```bash
python manage.py runserver
```

The API will be available at **http://127.0.0.1:8000/**

---

## API Endpoints

### Base URL: `http://127.0.0.1:8000/api/`

---

### `GET /api/`
API root with documentation overview.

**Response:**
```json
{
  "name": "YouTube Transcript API",
  "version": "1.0.0",
  "endpoints": { ... }
}
```

---

### `GET /api/transcript/<video_id>/`
Fetch the **default (best available)** transcript. Prefers manually created captions over auto-generated ones.

**Example:**
```
GET /api/transcript/dQw4w9WgXcQ/
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "video_id": "dQw4w9WgXcQ",
    "language": "English",
    "language_code": "en",
    "is_generated": false,
    "transcript": [
      {
        "text": "We're no strangers to love",
        "start": 18.16,
        "duration": 1.6
      },
      ...
    ],
    "full_text": "We're no strangers to love ..."
  }
}
```

**Not Found Response (404):**
```json
{
  "success": false,
  "error": {
    "code": "SUBTITLE_NOT_FOUND",
    "message": "No subtitle/transcript found for video 'abc123'."
  }
}
```

---

### `GET /api/transcript/<video_id>/languages/`
List all available transcript languages for a video.

**Example:**
```
GET /api/transcript/dQw4w9WgXcQ/languages/
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "video_id": "dQw4w9WgXcQ",
    "total_available": 3,
    "available_transcripts": {
      "manual": [
        {
          "language": "English",
          "language_code": "en",
          "is_generated": false,
          "is_translatable": true
        }
      ],
      "auto_generated": [
        {
          "language": "English (auto-generated)",
          "language_code": "en",
          "is_generated": true,
          "is_translatable": true
        }
      ]
    }
  }
}
```

---

### `GET /api/transcript/<video_id>/<language_code>/`
Fetch transcript for a **specific language**. If the exact language is not available but the video has a translatable transcript, it will return a translated version.

**Example:**
```
GET /api/transcript/dQw4w9WgXcQ/en/
GET /api/transcript/dQw4w9WgXcQ/fr/
GET /api/transcript/dQw4w9WgXcQ/de/
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "video_id": "dQw4w9WgXcQ",
    "language": "French",
    "language_code": "fr",
    "is_generated": false,
    "transcript": [ ... ],
    "full_text": "..."
  }
}
```

**Language Not Found (404):**
```json
{
  "success": false,
  "error": {
    "code": "SUBTITLE_NOT_FOUND",
    "message": "No subtitle found for video 'dQw4w9WgXcQ' in language 'jp'. Use /api/transcript/dQw4w9WgXcQ/languages/ to see available languages."
  }
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `SUBTITLE_NOT_FOUND` | 404 | No transcript available for this video/language |
| `SUBTITLES_DISABLED` | 404 | The video owner has disabled subtitles |
| `VIDEO_UNAVAILABLE` | 404 | Video doesn't exist or is private |
| `RETRIEVAL_FAILED` | 503 | YouTube is blocking or rate limiting |
| `INVALID_REQUEST` | 400 | Missing or invalid parameters |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Quick Test (curl)

```bash
# Default transcript
curl http://127.0.0.1:8000/api/transcript/dQw4w9WgXcQ/

# List languages
curl http://127.0.0.1:8000/api/transcript/dQw4w9WgXcQ/languages/

# English transcript
curl http://127.0.0.1:8000/api/transcript/dQw4w9WgXcQ/en/

# French transcript
curl http://127.0.0.1:8000/api/transcript/dQw4w9WgXcQ/fr/
```

---

## Production Notes

- Change `SECRET_KEY` in `settings.py` to a real secret (use environment variable)
- Set `DEBUG = False`
- Set `ALLOWED_HOSTS` to your domain
- Use `gunicorn` or `uwsgi` as the WSGI server
- Consider adding Redis-based caching to avoid repeated YouTube requests
