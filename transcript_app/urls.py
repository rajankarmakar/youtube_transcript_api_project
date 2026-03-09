from django.urls import path
from .views import (
    APIRootView,
    TranscriptDefaultView,
    TranscriptLanguageView,
    TranscriptLanguagesListView,
)

urlpatterns = [
    # API root - documentation overview
    path("", APIRootView.as_view(), name="api-root"),

    # GET /api/transcript/<video_id>/  → default transcript
    path(
        "transcript/<str:video_id>/",
        TranscriptDefaultView.as_view(),
        name="transcript-default",
    ),

    # GET /api/transcript/<video_id>/languages/  → list available languages
    path(
        "transcript/<str:video_id>/languages/",
        TranscriptLanguagesListView.as_view(),
        name="transcript-languages",
    ),

    # GET /api/transcript/<video_id>/<language_code>/  → transcript by language
    path(
        "transcript/<str:video_id>/<str:language_code>/",
        TranscriptLanguageView.as_view(),
        name="transcript-by-language",
    ),
]
