# views.py (add this view)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from myAgent.services.QueryService import QueryService

query_service = QueryService()

@api_view(['POST'])
def query_document(request):
    """
    Query a processed document.
    
    Request body:
    {
        "job_id": "uuid-string",
        "query": "What is the problem statement?",
        "top_k": 5,  # optional, default 5
        "similarity_threshold": 0.3,  # optional, default 0.3
        "include_sources": true  # optional, default true
    }
    """
    try:
        job_id = request.data.get('job_id')
        query = request.data.get('query')
        top_k = request.data.get('top_k', 5)
        similarity_threshold = request.data.get('similarity_threshold', 0.3)
        include_sources = request.data.get('include_sources', True)
        
        if not job_id:
            return Response(
                {"error": "job_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not query:
            return Response(
                {"error": "query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = query_service.query_document(
            job_id=job_id,
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            include_sources=include_sources
        )
        
        if result.get("success"):
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )