from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Profile
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .serializers import ProfileSerializers
from user_account.models import CustomUser
from user_account.serialializers import customuserserializer
from rest_framework import status


class UserProfileView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
           profile_data=Profile.objects.get(user=request.user)
        except:
            return Response({"message":"no user found"},status=status.HTTP_204_NO_CONTENT)
        ser=ProfileSerializers(profile_data)
        return Response(ser.data)
    def post(self,request):
        profile_data=request.data
        profile_data['user']=request.user.id
        print("userr===============================================================",request.user.id,flush=True)
        ser=ProfileSerializers(data=profile_data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)
    def patch(self,request):
        updated_profile_data=request.data
        try:
            instance_profile_data=Profile.objects.get(user=request.user)
        except:
            return Response("no profile found")
        ser=ProfileSerializers(instance_profile_data,data=updated_profile_data,partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)
    


class SelfUser(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user=CustomUser.objects.get(email=request.user) 
        ser=customuserserializer(user)
        return Response(ser.data)
