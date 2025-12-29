from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "email and password required"}, status=400)

        if User.objects.filter(username=email).exists():
            return Response({"error": "user already exists"}, status=400)

        user = User.objects.create_user(username=email, email=email, password=password)
        return Response({"id": user.id, "email": user.email}, status=201)

class MeView(APIView):
    def get(self, request):
        u = request.user
        return Response({"id": u.id, "email": u.email})
