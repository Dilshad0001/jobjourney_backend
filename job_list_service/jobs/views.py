from django.shortcuts import render
from .models import JobApplication
from rest_framework.views import APIView
from .serializers import JobListSerializer
from rest_framework.response import Response
from rest_framework import status
import requests
import traceback 
import logging 
from rest_framework.permissions import IsAuthenticated
from . authentication import CustomAuthentication

logger = logging.getLogger(__name__)


class JobListView(APIView):
    authentication_classes = [CustomAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        # candidate_id=request.GET.get('candidateId')
        candidate_id=request.user.id
        app_status=request.GET.get('status')
        if app_status:
            job_list=JobApplication.objects.filter(candidate_id=candidate_id,status=app_status)        
        else:
            job_list=JobApplication.objects.filter(candidate_id=candidate_id)
        ser=JobListSerializer(job_list, many=True)
        return Response({"message":"Data fetched successfully","data":ser.data},status=status.HTTP_200_OK)
    
    # def post(self,request):
    #     new_job=request.data
    #     token=new_job['candidate_id']
    #     headers = {'Authorization': f'Bearer {token}'}
    #     try:
    #         res=request.get('http://localhost/auth/api/auth/me/',headers=headers)
    #     except Exception as e:
    #         print("error in calling auth service")    
    #     new_job['candidate_id']=res.id    

    #     ser=JobListSerializer(data=new_job)
    #     if ser.is_valid():
    #         ser.save()
    #         return Response({"message":"ne application added successfully","data":ser.data},status=status.HTTP_201_CREATED)
    #     return Response({"message":"new job application added failed","error":ser.errors},status=status.HTTP_400_BAD_REQUEST)
    def post(self, request):
        print("enterd=1",request.user)
        user_id = request.user.id 
        print("enterd=2", user_id)
        data = request.data.copy()
        data['candidate_id'] = user_id
        print("enetrd=3= = ==",data)

        ser = JobListSerializer(data=data)
        if ser.is_valid():
            ser.save()
            return Response({"message": "New job application added successfully", "data": ser.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "New job application failed", "error": ser.errors}, status=status.HTTP_400_BAD_REQUEST)

    # def post(self, request):
    #     print("enterd in post==1")
    #     user_id=request.user.id
    #     token = request.headers.get('Authorization')
    #     print("enterd in post==2")  
    #     print("token== ==",token)

    #     if not token:
    #         print("enterd in post==3")
    #         return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    #     print("enterd in post==4")
    #     headers = {'Authorization': token}
    #     print("enterd in post==5")
    #     try:
    #         print("enterd in post==6")
    #         res = requests.get("http://api_gateway/auth/api/auth/me/", headers=headers,timeout=3)  # use internal Docker host
    #         print("enterd in post==7")
    #         if res.status_code != 200:
    #             print("enterd in post==8")
    #             return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    #         print("enterd in post==9")
    #         user_data = res.json()
    #         user_id = user_data.get('id')
    #         print("enterd in post==10===",user_data)
    #     except Exception as e:
    #         logger.error("Error contacting auth service", exc_info=True)  # 🔄 CHANGE: Log full traceback
    #         return Response({"error": "Auth service error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #     # Now add the user_id to request data
    #     data = request.data.copy()
    #     data['candidate_id'] = user_id

    #     ser = JobListSerializer(data=data)
    #     if ser.is_valid():
    #         ser.save()
    #         return Response({"message": "New job application added successfully", "data": ser.data}, status=status.HTTP_201_CREATED)
    #     return Response({"message": "New job application failed", "error": ser.errors}, status=status.HTTP_400_BAD_REQUEST)    
    
    def patch(self,request):
        job_id=request.GET.get('jobId')
        try:
            selected_job=JobApplication.objects.get(id=job_id)
        except JobApplication.DoesNotExist:
            return Response({"message": "Job application not found"},status=status.HTTP_404_NOT_FOUND)
        ser=JobListSerializer(selected_job,request.data,partial=True)
        if ser.is_valid():
            ser.save()
            return Response({"message":"job application updated successfully","data":ser.data},status=status.HTTP_200_OK)
        return Response({"message":"job application update failed","error":ser.errors},status=status.HTTP_400_BAD_REQUEST)
