from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def Home(request):
    return HttpResponse("hi this is Accounts app")

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,LoginSerializer,ProfileSerializer,UpdateSerializer

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .throttles import LoginRateThrottle, RegisterRateThrottle

class RegisterAPIView(APIView):
    throttle_classes=[RegisterRateThrottle]

    @extend_schema(
            request=RegisterSerializer,
            responses={
                201: RegisterSerializer,
                400: OpenApiResponse(
                    description='Validation error'
                ),
            },
            description='Register a new user'
    )

    def post(self,request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                RegisterSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
from django.contrib.auth import authenticate,login,logout
from rest_framework_simplejwt.tokens import RefreshToken

class LoginAPIVies(APIView):
    throttle_classes=[LoginRateThrottle]

    @extend_schema(
        request=LoginSerializer,
            responses={
                201: LoginSerializer,
                400: OpenApiResponse(
                    description='credentials error'
                ),
            },
            description='logined user'
        )

    def post(self,request):
        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        login(request,user)        
        return Response(
            {
                "message": "login success"
            },
            status=status.HTTP_200_OK,)
            

from rest_framework.permissions import IsAuthenticated
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            201: OpenApiResponse(
                description='logout successfully'
            ),
            400: OpenApiResponse(
                description='Authentication credentials were not provided'
            ),
        },
        description='logout user'
    )
    

    def post(self,request):
        logout(request)
        return Response(
            {
                "message": "Logged Out Successfully"
            },
            status=status.HTTP_200_OK
        )


class Profile(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProfileSerializer,
            responses={
                201: OpenApiResponse(
                    description='profile  success'
                ),
                400: OpenApiResponse(
                    description='profile error'
                ),
            },
            description='profile user'
    )
    

    def get(self,request):
        serializer = ProfileSerializer(request.user)
        
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            )
        
class Update(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UpdateSerializer,
            responses={
                201: OpenApiResponse(
                    description='updated successfully'
                ),
                400: OpenApiResponse(
                    description='update error'
                ),
            },
            description='updated user'
    )
    

    def patch(self,request):
        serializer = UpdateSerializer(request.user,data=request.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message" : "Updated Profile",
                  "data" : serializer.data,},
               
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )