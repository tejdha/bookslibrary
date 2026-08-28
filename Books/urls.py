from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('books',views.BooksViewSet,basename='book')

urlpatterns = [
    path('home/',views.Home),
    path('myactivity/',views.ListActivity.as_view()),
] + router.urls
