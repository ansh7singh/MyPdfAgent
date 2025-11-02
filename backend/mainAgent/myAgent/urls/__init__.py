from django.urls import path, include
from . import uploadUrls

urlpatterns = [
    path('', include(uploadUrls)),
]
