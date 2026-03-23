"""
Service layer for YouTube transcript fetching.
Uses Webshare proxy to avoid YouTube IP blocks on cloud servers.
"""
import os
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)
from youtube_transcript_api.proxies import WebshareProxyConfig


def _build_api() -> YouTubeTranscriptApi:
    webshare_user = os.getenv("WEBSHARE_USERNAME")
    webshare_pass = os.getenv("WEBSHARE_PASSWORD")

    if webshare_user and webshare_pass:
        print("[Transcript] Using Webshare proxy.")
        proxy_config = WebshareProxyConfig(
            proxy_username=webshare_user,
            proxy_password=webshare_pass,
        )
        return YouTubeTranscriptApi(proxy_config=proxy_config)

    print("[Transcript] WARNING: No proxy configured. YouTube may block requests.")
    return YouTubeTranscriptApi()


_api = _build_api()


class TranscriptService:

    @staticmethod
    def list_available_transcripts(video_id: str) -> dict:
        transcript_list = _api.list(video_id)

        available = {"manual": [], "auto_generated": []}
        for transcript in transcript_list:
            entry = {
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable,
            }
            if transcript.is_generated:
                available["auto_generated"].append(entry)
            else:
                available["manual"].append(entry)

        return available

    @staticmethod
    def get_default_transcript(video_id: str) -> dict:
        transcript_list = _api.list(video_id)

        try:
            transcript = transcript_list.find_manually_created_transcript(
                [t.language_code for t in transcript_list]
            )
        except NoTranscriptFound:
            transcript = transcript_list.find_generated_transcript(
                [t.language_code for t in transcript_list]
            )

        fetched = transcript.fetch()

        return {
            "video_id": video_id,
            "language": fetched.language,
            "language_code": fetched.language_code,
            "is_generated": fetched.is_generated,
            "transcript": [
                {
                    "text": s.text,
                    "start": round(s.start, 2),
                    "duration": round(s.duration, 2),
                }
                for s in fetched.snippets
            ],
            "full_text": " ".join(s.text for s in fetched.snippets),
        }

    @staticmethod
    def get_transcript_by_language(video_id: str, language_code: str) -> dict:
        transcript_list = _api.list(video_id)

        try:
            transcript = transcript_list.find_transcript([language_code])
        except NoTranscriptFound:
            for t in transcript_list:
                if t.is_translatable:
                    transcript = t.translate(language_code)
                    break
            else:
                raise NoTranscriptFound(video_id, [language_code], transcript_list)

        fetched = transcript.fetch()

        return {
            "video_id": video_id,
            "language": fetched.language,
            "language_code": fetched.language_code,
            "is_generated": fetched.is_generated,
            "transcript": [
                {
                    "text": s.text,
                    "start": round(s.start, 2),
                    "duration": round(s.duration, 2),
                }
                for s in fetched.snippets
            ],
            "full_text": " ".join(s.text for s in fetched.snippets),
        }
