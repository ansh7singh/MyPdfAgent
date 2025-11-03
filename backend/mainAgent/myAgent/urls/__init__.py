from django.urls import path, include
from myAgent.views.queryView import query_document

urlpatterns = [
    # Include the upload URLs
    path('', include('myAgent.urls.uploadUrls')),
    
    # Add the query endpoint directly
    path('query/', query_document, name='query_document'),
]