from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User
from rest_framework.decorators import api_view
from datetime import datetime


class UserViewSet(viewsets.ModelViewSet):
    """
    User List - Prueba Final DevOps
    
    Esta API es para gestionar usuarios..
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_view_name(self):
        """Personalizar el nombre que aparece en la página HTML de DRF"""
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        return f"User List - Ambiente Desarrollo - {fecha_actual}"

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data

        if self.get_queryset().filter(dni=data.get('dni')).exists():
            return Response(
                {'detail': 'User already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})
