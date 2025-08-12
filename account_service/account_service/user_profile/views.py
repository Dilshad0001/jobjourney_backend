from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Profile
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.decorators import permission_classes
from .serializers import ProfileSerializers
from user_account.models import CustomUser
from user_account.serialializers import customuserserializer
from rest_framework import status
from rest_framework.exceptions import NotFound


class UserProfileView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        profileSearch=request.GET.get('search')
        profile_id=request.GET.get('profileId')
        print('PROFILE ID=',profile_id)
        if profileSearch:
            if profileSearch=="all":
                profile_data=Profile.objects.all().exclude(user=request.user)    
            else:
                profile_data=Profile.objects.filter(full_name__istartswith=profileSearch).exclude(user=request.user)
            ser=ProfileSerializers(profile_data,many=True)
            return Response({"message":"successfully fetched all users","data":ser.data},status=status.HTTP_200_OK)

        if profile_id:
            try:
                profile_data = Profile.objects.get(id=profile_id)
                ser = ProfileSerializers(profile_data)
                return Response(ser.data)
            except Profile.DoesNotExist:
                raise NotFound(detail="Profile not found", code=404)

        try:
           profile_data=Profile.objects.get(user=request.user)
           ser=ProfileSerializers(profile_data)
           return Response(ser.data)
        except:
            return Response({"message":"no user found"},status=status.HTTP_204_NO_CONTENT)

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


class AdminProfileListView(APIView):
    permission_classes=[IsAdminUser]
    def get(self,request):
        name_search=request.GET.get('full_name')
        if name_search:
            profile_list=Profile.objects.filter(full_name__istartswith=name_search)
        else:
            profile_list=Profile.objects.all()
        ser=ProfileSerializers(profile_list,many=True)
        return Response({"message":"profile list fetched successfully","data":ser.data},status=status.HTTP_200_OK)


class AdmindashBoard(APIView):
    # permission_classes=[IsAuthenticated]
    permission_classes=[IsAdminUser]
    def get(self,request):
        user_count=CustomUser.objects.all().count()
        profile_count=Profile.objects.all().count()
        return Response({"user_count":user_count,"profile_count":profile_count})        
               
# from rest_framework.pagination import LimitOffsetPagination
# class AdminProfileListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         name_search = request.GET.get('full_name')
#         profiles = Profile.objects.all()

#         if name_search:
#             profiles = profiles.filter(full_name__istartswith=name_search)

#         # Apply pagination
#         paginator = LimitOffsetPagination()
#         result_page = paginator.paginate_queryset(profiles, request, view=self)

#         serializer = ProfileSerializers(result_page, many=True)

#         return paginator.get_paginated_response(serializer.data)