"""
API Views for YouTube Transcript endpoints.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from youtube_transcript_api import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)

from .services import TranscriptService


def _error_response(message: str, code: str, http_status: int) -> Response:
    return Response(
        {"success": False, "error": {"code": code, "message": message}},
        status=http_status,
    )


class TranscriptDefaultView(APIView):
    """
    GET /api/transcript/<video_id>/
    Returns the default (best available) transcript for the given YouTube video ID.
    """

    def get(self, request, video_id: str):
        video_id = video_id.strip()
        if not video_id:
            return _error_response(
                "video_id is required.",
                "INVALID_REQUEST",
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            data = TranscriptService.get_default_transcript(video_id)
            return Response({"success": True, "data": data}, status=status.HTTP_200_OK)

        except VideoUnavailable:
            return _error_response(
                f"The video '{video_id}' is unavailable or does not exist.",
                "VIDEO_UNAVAILABLE",
                status.HTTP_404_NOT_FOUND,
            )
        except TranscriptsDisabled:
            return _error_response(
                f"Subtitles are disabled for video '{video_id}'.",
                "SUBTITLES_DISABLED",
                status.HTTP_404_NOT_FOUND,
            )
        except NoTranscriptFound:
            return _error_response(
                f"No subtitle/transcript found for video '{video_id}'.",
                "SUBTITLE_NOT_FOUND",
                status.HTTP_404_NOT_FOUND,
            )
        except CouldNotRetrieveTranscript as e:
            return _error_response(
                f"Could not retrieve transcript for video '{video_id}': {str(e)}",
                "RETRIEVAL_FAILED",
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            return _error_response(
                f"An unexpected error occurred: {str(e)}",
                "INTERNAL_ERROR",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TranscriptLanguageView(APIView):
    """
    GET /api/transcript/<video_id>/<language_code>/
    Returns the transcript for the given YouTube video ID in the specified language.
    Example: /api/transcript/dQw4w9WgXcQ/fr/  → French transcript
    """

    def get(self, request, video_id: str, language_code: str):
        video_id = video_id.strip()
        language_code = language_code.strip().lower()

        if not video_id:
            return _error_response(
                "video_id is required.",
                "INVALID_REQUEST",
                status.HTTP_400_BAD_REQUEST,
            )
        if not language_code:
            return _error_response(
                "language_code is required.",
                "INVALID_REQUEST",
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            data = TranscriptService.get_transcript_by_language(video_id, language_code)
            return Response({"success": True, "data": data}, status=status.HTTP_200_OK)

        except VideoUnavailable:
            return _error_response(
                f"The video '{video_id}' is unavailable or does not exist.",
                "VIDEO_UNAVAILABLE",
                status.HTTP_404_NOT_FOUND,
            )
        except TranscriptsDisabled:
            return _error_response(
                f"Subtitles are disabled for video '{video_id}'.",
                "SUBTITLES_DISABLED",
                status.HTTP_404_NOT_FOUND,
            )
        except NoTranscriptFound:
            return _error_response(
                f"No subtitle found for video '{video_id}' in language '{language_code}'. "
                f"Use /api/transcript/{video_id}/languages/ to see available languages.",
                "SUBTITLE_NOT_FOUND",
                status.HTTP_404_NOT_FOUND,
            )
        except CouldNotRetrieveTranscript as e:
            return _error_response(
                f"Could not retrieve transcript: {str(e)}",
                "RETRIEVAL_FAILED",
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            return _error_response(
                f"An unexpected error occurred: {str(e)}",
                "INTERNAL_ERROR",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TranscriptLanguagesListView(APIView):
    """
    GET /api/transcript/<video_id>/languages/
    Lists all available transcript languages for a video.
    """

    def get(self, request, video_id: str):
        video_id = video_id.strip()
        if not video_id:
            return _error_response(
                "video_id is required.",
                "INVALID_REQUEST",
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            available = TranscriptService.list_available_transcripts(video_id)
            total = len(available["manual"]) + len(available["auto_generated"])
            return Response(
                {
                    "success": True,
                    "data": {
                        "video_id": video_id,
                        "total_available": total,
                        "available_transcripts": available,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except VideoUnavailable:
            return _error_response(
                f"The video '{video_id}' is unavailable or does not exist.",
                "VIDEO_UNAVAILABLE",
                status.HTTP_404_NOT_FOUND,
            )
        except TranscriptsDisabled:
            return _error_response(
                f"Subtitles are disabled for video '{video_id}'.",
                "SUBTITLES_DISABLED",
                status.HTTP_404_NOT_FOUND,
            )
        except NoTranscriptFound:
            return _error_response(
                f"No subtitles/transcripts found for video '{video_id}'.",
                "SUBTITLE_NOT_FOUND",
                status.HTTP_404_NOT_FOUND,
            )
        except CouldNotRetrieveTranscript as e:
            return _error_response(
                f"Could not retrieve transcript list: {str(e)}",
                "RETRIEVAL_FAILED",
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            return _error_response(
                f"An unexpected error occurred: {str(e)}",
                "INTERNAL_ERROR",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class APIRootView(APIView):
    """
    GET /api/
    Returns API documentation overview.
    """

    def get(self, request):
        base = request.build_absolute_uri("/api/")
        return Response(
            {
                "name": "YouTube Transcript API",
                "version": "1.0.0",
                "description": "Fetch YouTube video subtitles/transcripts by video ID.",
                "endpoints": {
                    "get_default_transcript": {
                        "url": f"{base}transcript/<video_id>/",
                        "method": "GET",
                        "description": "Get default (best available) transcript for a video.",
                        "example": f"{base}transcript/dQw4w9WgXcQ/",
                    },
                    "list_languages": {
                        "url": f"{base}transcript/<video_id>/languages/",
                        "method": "GET",
                        "description": "List all available transcript languages for a video.",
                        "example": f"{base}transcript/dQw4w9WgXcQ/languages/",
                    },
                    "get_transcript_by_language": {
                        "url": f"{base}transcript/<video_id>/<language_code>/",
                        "method": "GET",
                        "description": "Get transcript for a specific language.",
                        "example": f"{base}transcript/dQw4w9WgXcQ/en/",
                    },
                },
            },
            status=status.HTTP_200_OK,
        )
