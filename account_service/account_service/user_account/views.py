from django.shortcuts import render
from rest_framework.views import APIView
from .models import CustomUser
from .serialializers import RequestOtpSerializer,customuserserializer
from rest_framework.response import Response
import random
from .tasks import send_otp_email
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from user_profile.models import Profile
from user_profile.serializers import ProfileSerializers


class RequestOtpView(APIView):
    def post(self,request):
        ser=RequestOtpSerializer(data=request.data)
        if ser.is_valid():
            email=ser.validated_data['email']
            user,created=CustomUser.objects.get_or_create(email=email)
            otp=str(random.randint(1000,9999))
            user.otp=otp
            user.save()
            send_otp_email.delay(user.email,otp)
            return Response ("otp send to email")
        return Response(ser.errors)


class VerifyOtpView(APIView):
    def post(self,request):
        email=request.data.get('email')
        otp_code=request.data.get('otp') 
        try:
            user=CustomUser.objects.get(email=email)
            print("user=====",user)
        except CustomUser.DoesNotExist:
            return Response('user not found')  
        if user.otp !=otp_code:
            return Response('invalid otp')
        user.otp=None
        user.save()
        refresh =RefreshToken.for_user(user)
        return Response({
            "refresh":str(refresh),
            "access":str(refresh.access_token),
            "is_admin":user.is_admin,
        })




# user_account/views.py
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.exceptions import ValidationError


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

class GoogleLoginAPIView(APIView):
    def post(self, request):
        token = request.data.get('credential')

        if not token:
            return Response({"error": "No token provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the token with Google
        google_response = requests.get(
            f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
        )
        if google_response.status_code != 200:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        user_info = google_response.json()
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')

        user,created=CustomUser.objects.get_or_create(email=email)
        print("user=========================================================================================================",user,flush=True)

        refresh=RefreshToken.for_user(user)

        # Here, you could create the user in your DB if you want

        return Response({
            "email": email,
            "name": name,
            "picture": picture,
            "google_token": token,
            "access_token":str(refresh.access_token),
            "refresh_token":str(refresh)
        })


# class meView(APIView):


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class GitHubLoginAPIView(APIView):
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "No code provided"}, status=400)

        # Exchange code for access token
        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        if token_response.status_code != 200:
            return Response({"error": "Failed to fetch access token"}, status=400)

        access_token = token_response.json().get("access_token")
        if not access_token:
            return Response({"error": "No access token returned"}, status=400)

        # Fetch user info
        user_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"},
        )
        if user_response.status_code != 200:
            return Response({"error": "Failed to fetch user info"}, status=400)

        user_data = user_response.json()
        email = user_data.get("email")
        username = user_data.get("login")

        # If email missing, fetch emails
        if not email:
            emails_response = requests.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"token {access_token}"},
            )
            emails = emails_response.json()
            primary_emails = [e for e in emails if e.get("primary")]
            if primary_emails:
                email = primary_emails[0].get("email")
        if not email:
            return Response({"error": "Email not available"}, status=400)

        # Create or get user
        user, created = CustomUser.objects.get_or_create(email=email)

        # Generate auth token
        token, _ = Token.objects.get_or_create(user=user)
        print("user=========================================================================================================",user,flush=True)
        Refresh=RefreshToken.for_user(user)
        return Response({"token": token.key,
                         "access_token":str(Refresh.access_token),
                         "refresh_token":str(Refresh),
                         })



from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class selfUser(APIView):
    permission_classes=[IsAuthenticated] 
    def get(self,request):
        print("===== DEBUG =======================")
        print("request-user",request.user)
        print("Request headers:", request.headers)
        print("Authorization header:", request.headers.get("Authorization"))
        print("=================")

        try:
            self=CustomUser.objects.get(id=request.user.id)
        except CustomUser.DoesNotExist:
            return Response({"mesage user not found"},status=status.HTTP_404_NOT_FOUND)
        ser=customuserserializer(self)
        return Response({"message":"self user fetched successfully","data":ser.data},status=status.HTTP_200_OK)


class selfProfile(APIView):
    permission_classes=[IsAuthenticated] 
    def get(self,request):
        try:
            self=Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({"mesage user profile not found"},status=status.HTTP_404_NOT_FOUND)
        ser=ProfileSerializers(self)
        return Response({"message":"self user profile fetched successfully","data":ser.data},status=status.HTTP_200_OK)
    

class AdminUserListView(APIView):
    # permission_classes=[IsAuthenticated]
    def get(self,request):
        email_search=request.GET.get('email')
        if email_search:
            user_list=CustomUser.objects.filter(email__istartswith=email_search).exclude(is_admin=True)
        else:
            user_list=CustomUser.objects.all().exclude(is_admin=True)
        ser=customuserserializer(user_list,many=True)
        return Response({"message":"user list fetched successfully","data":ser.data},status=status.HTTP_200_OK)
               
