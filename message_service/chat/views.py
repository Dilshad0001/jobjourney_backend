from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response  import Response
from . models import Message,ChatContact
from rest_framework.permissions import IsAuthenticated
from .serialisers import MessageSerializer,ChatContactserialser
from .authentication import CustomAuthentication
import requests
from rest_framework import status


class hello(APIView):
    def get(delf,request):
        k="hello world"
        return Response(k)

class ChatHistoryView(APIView):
    authentication_classes = [CustomAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user1 = request.GET.get("user1")
        user2 = request.GET.get("user2")


        messages = Message.objects.filter(
            sender_id__in=[user1, user2],
            receiver_id__in=[user1, user2]
        ).order_by("timestamp")

        # ❌ Problem: You probably had `return messages`
        # ✅ Fix:
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)





class ContactListView(APIView):
    authentication_classes = [CustomAuthentication]
    permission_classes = [IsAuthenticated]  
    def get_authenticated_user_data(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                response = requests.get(
                    "http://51.21.215.128/auth/api/auth/self-profile/",
#                    'http://51.21.215.128/auth/api/auth/self-profile/',
                    headers={'Authorization': auth_header}
                )
                if response.status_code == 200:
                    return response.json().get('data')
            except requests.exceptions.RequestException as e:
                print("Error calling internal API:", e)
        return None



    def get(self, request):
        actual_data = self.get_authenticated_user_data(request)
        if not actual_data:
            return Response({"error": "Unable to authenticate user"}, status=401)

        contact_list = ChatContact.objects.filter(user_id=actual_data.get('id')).order_by('-last_message_at')
        ser = ChatContactserialser(contact_list, many=True)
        return Response({"message": "Contact list fetched successfully", "data": ser.data}, status=status.HTTP_200_OK)


    def post(self, request):
        actual_data = self.get_authenticated_user_data(request)
        autHeader = request.headers.get('Authorization')
        if not actual_data:
            return Response({"error": "Unable to authenticate user"}, status=401)

        new_contact = request.data.copy()
        if not new_contact.get('contact_id'):
            return Response({"error": "contact_id is required"}, status=400)

        new_contact['user_id'] = actual_data.get('id')
        reciver_id=new_contact.get('contact_id')
        print('RECIVER ID  IN CONTACT LIST VIEW==',reciver_id)
        try:
            response = requests.get(
                f"http://51.21.215.128/auth/user/profile/?profileId={reciver_id}",
                headers={'Authorization': autHeader}
            )
            print('STATUS IN CONTACT LIST VIEW=',response.status_code)
            if response.status_code == 200:
                # return response.json().get('data')
                data=response.json()
                print('DATA IN CONTACT LIST VIEW==',data)
                new_contact['contact_name']=data['full_name']
        except requests.exceptions.RequestException as e:
            print("Error calling internal API:", e)

        print('NEW CONTACT IN CONTACT LIST VIEW=',new_contact)
        ser = ChatContactserialser(data=new_contact)
        if ser.is_valid():
            ser.save()
            return Response({"message": "new chat contact added successfully", "data": ser.data}, status=201)
        return Response({"message": "chat contact add failed", "error": ser.errors}, status=400)
    
    def patch(self,request):
        print ('ENTERD IN COUNT REST PATCH')
        userId=request.GET.get('user_id')
        contactId=request.GET.get('contact_id')
        try:
            chat_contact=ChatContact.objects.get(user_id=userId,contact_id=contactId)
        except ChatContact.DoesNotExist:
            return Response({"error": "Chat contact not found."}, status=status.HTTP_404_NOT_FOUND)        
        ser=ChatContactserialser(chat_contact,request.data,partial=True)
        if ser.is_valid():
            ser.save()
            return Response({"message":"data updated successfully","data":ser.data},status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid data", "error": ser.errors},status=status.HTTP_400_BAD_REQUEST)    
            

    def delete(self, request):
        actual_data = self.get_authenticated_user_data(request)
        if not actual_data:
            return Response({"error": "Unable to authenticate user"}, status=401)

        user_id = actual_data.get('id')
        contact_id = request.data.get('contact_id') or request.GET.get('contact_id')

        if not contact_id:
            return Response({"error": "contact_id is required"}, status=400)

        try:
            chat_contact = ChatContact.objects.get(user_id=user_id, contact_id=contact_id)
            chat_history=Message.objects.filter(sender_id=user_id, receiver_id=contact_id)
            chat_contact.delete()
            chat_history.delete()
            return Response({"message": "Chat contact deleted successfully"}, status=status.HTTP_200_OK)
        except ChatContact.DoesNotExist:
            return Response({"error": "Chat contact not found"}, status=status.HTTP_404_NOT_FOUND)
