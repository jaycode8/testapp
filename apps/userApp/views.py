import os
from random import randint
from datetime import datetime
import re
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from .models import Users
from .serializers import usersSerializer
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from .utils.emails import transporter
from cloudinary.uploader import destroy, upload

OTP = None


def customErrorMessage(error_data):
    error_messages = error_data.get("error", {})
    error_message = None
    for field, messages in error_messages.items():
        if messages:
            error_message = messages[0]
        return error_message
        break


def listOfUsers():
    user = Users.objects.all().exclude(is_superuser=True)
    serializer = usersSerializer(user, many=True)
    return Response({"message": "list of all users", "data": serializer.data, "status": status.HTTP_200_OK})


def signUp(req):
    serializer = usersSerializer(data=req.data)
    global OTP
    global username
    if serializer.is_valid():
        instance = serializer.save()
        upload_file = req.FILES['profile']
        result = upload(upload_file, folder="django_users")
        img_url = result['url']
        instance.pic = img_url
        instance.save()
        OTP = randint(1000, 9999)
        username = serializer.data["username"]
        transporter(serializer.data["email"], OTP)
        # print(OTP)
        return Response({"message": "An OTP verification code has been sent to your email", "success": "true", "status": status.HTTP_200_OK, "OTP": OTP})
    return Response({"message": customErrorMessage({"error": serializer.errors}), "success": "false", "status": status.HTTP_400_BAD_REQUEST})


def verifyOTP(req):
    global OTP
    global username
    if OTP == int(req.data["otp"]):
        instance = Users.objects.get(username=username)
        instance.is_active = True
        instance.save()
        return Response({"message": "User successfully added to the system", "success": "true", "status": status.HTTP_200_OK})
    return Response({"message": "Incorrect Code", "success": "false", "status": status.HTTP_400_BAD_REQUEST})


def signIn(req):
    user = req.data
    try:
        usr = get_object_or_404(Users, username=user['uname'])
    except:
        return Response({"message": "Username does not exist", "success": "false", "status": status.HTTP_400_BAD_REQUEST})
    if not usr.is_active:
        return Response({"message": "Account does not exist", "success": "false", "status": status.HTTP_400_BAD_REQUEST})
    found_user = authenticate(username=user['uname'], password=user['passw'])
    if not found_user:
        return Response({"message": "The password is incorect", "success": "false", "status": status.HTTP_400_BAD_REQUEST})

    if usr.is_superuser:
        return Response({"message": "admin logged in"})
    token, created = Token.objects.get_or_create(user=usr)
    token.created = datetime.now()
    token.save()
    serializer = usersSerializer(instance=usr)
    return Response({"message": "Successfully loged into your account", "user":"", "success": "true", "token": token.key, "status": status.HTTP_200_OK})


def modifyUser(req, obj):
    serializer = usersSerializer(obj, data=req.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Successfully appdated your account infor", "success": "true"})
    return Response({"message": customErrorMessage({"error": serializer.errors}), "success": "false"})


def removeAccount(obj):
    img_url = obj.pic
    obj.delete()
    if img_url:
        public_id = img_url.split('/')[-1].split('.')[0]
        destroy(f"django_users/{public_id}")
        print("successfully removed image")
    return Response({"message": "Account deleted", "success": "true", "status": "true"})


@api_view(["POST"])
def verification(req):
    return verifyOTP(req)


@api_view(['GET', 'POST'])
def users_view(req):
    if req.method == 'GET':
        return listOfUsers()

    elif req.method == 'POST':
        return signUp(req)

    return Response({"message": "method not allowed", "status": status.HTTP_400_BAD_REQUEST})


@api_view(['POST'])
def signin_view(req):
    if req.method == "POST":
        return signIn(req)


@api_view(["GET", "PATCH", "PUT", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_view(req):
    user_data = usersSerializer(instance=req.user)
    user_obj = Users.objects.get(_id=req.user._id)
    if req.method == "GET":
        return Response({"message": f"{req.user}'s data Successfully fetched", "success": "true", "user": user_data.data, "status": status.HTTP_200_OK})

    elif req.method == 'PATCH':
        return modifyUser(req, user_obj)

    elif req.method == 'DELETE':
        return removeAccount(user_obj)


def testOTP(req):
    global OTP
    OTP = randint(1000, 9999)
    return Response({"message": "sent an otp to verify later", "OTP": OTP})


def testgetOTP(req):
    global OTP
    global user_infor
    return Response({"message": "Got the OTP from previous method", "OTP": OTP, "user": user_infor})


@api_view(["GET", "POST"])
def test(req):
    if req.method == "GET":
        return testgetOTP(req)
    elif req.method == "POST":
        return testOTP(req)
