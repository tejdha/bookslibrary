from django.urls import path
from . import views


urlpatterns = [
    path('',views.Home),
    path('register/',views.RegisterAPIView.as_view()),
    path('login/',views.LoginAPIVies.as_view()),
    path('logout/',views.LogoutAPIView.as_view()),
    path('profile/',views.Profile.as_view()),
    path('update/',views.Update.as_view()),
] 