from django.urls import path, include

urlpatterns = [
    path('api/', include('transcript_app.urls')),
]
