from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from .models import Category,Book,ActivityLog
from .serializers import BookCreateSerialzier,BookDetailsSerializer,BookListSerializer,ActivitySerializer,BookUpdateSerializer

# Create your views here.

def Home(request):
    return HttpResponse("hello this is books app")


from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import BookPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsOwner

from django.core.cache import cache
from .cache_utils import invalidate_books_cache,BOOKS_CACHE_VERSION_KEY

import logging

logger = logging.getLogger(__name__)

class BooksViewSet(ModelViewSet):

    queryset = Book.objects.all()   
    filter_backends = [SearchFilter,DjangoFilterBackend,OrderingFilter]
    pagination_class = BookPagination

    search_fields = ['title','author']
    filterset_fields = ['category']
    ordering_fields = ['title','pages','uploaded_time']

    def update(self, request, *args, **kwargs):
         # Treat PUT as partial update.
        # Note: DRF Browsable API may still submit an empty file input,
        # but React/Postman clients that omit the pdf field work correctly.
        print(request.data)
        # kwargs['partial'] = True
        response =  super().update(request, *args, **kwargs)

        invalidate_books_cache()
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)

        invalidate_books_cache()
        return response

    def get_serializer_class(self):
        if self.action == 'create':
            return BookCreateSerialzier
        
        elif self.action in ['update','partial_update']:
            return BookUpdateSerializer
        
        elif self.action in ('list','my_books'):
            return BookListSerializer
        
        return BookDetailsSerializer
    
    def get_permissions(self):
        if self.action in ('list','retrieve'):
            return [AllowAny()]
        elif self.action in ('create','my_books'):
            return [IsAuthenticated()]
        return [IsAuthenticated(),IsOwner()]

    def perform_create(self, serializer):
        book = serializer.save(uploaded_by=self.request.user)
        invalidate_books_cache()
        logger.info(
            "Book created : id=%s by user=%s",
            book.id,
            self.request.user.id
        )

    @action(
        detail = False,
        methods = ["get"]

    )
    def my_books(self,request):
        books = Book.objects.filter(uploaded_by=self.request.user)
        serializer = BookListSerializer(books,many=True)

        return Response(
            serializer.data
        )

    def list(self, request, *args, **kwargs):        
        
        version = cache.get(BOOKS_CACHE_VERSION_KEY,1)

        cache_key = f'books : {version} : {request.get_full_path()}'

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            logger.debug("Cache hit: %s", cache_key)
            return Response(cached_data)

        logger.debug("Cache miss : %s",cache_key)
        response = super().list(request, *args, **kwargs)

        cache.set(
            cache_key,
            response.data,
            timeout=300)

        return response

    def perform_destroy(self, instance):
        instance.delete()
        invalidate_books_cache()

from rest_framework.generics import ListAPIView
    
class ListActivity(ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ActivityLog.objects.filter(
            user=self.request.user).order_by("-created_at")




