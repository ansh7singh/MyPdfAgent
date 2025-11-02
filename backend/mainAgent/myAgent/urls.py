from django.urls import path, include

urlpatterns = [
    path('', include('myAgent.urls')),  # Include all URLs from the urls module
]
