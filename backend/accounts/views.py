from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Shop


class LoginView(APIView):
    """
    Uncle enters username + password.
    We check credentials, start a session, return shop info.
    """
    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Django checks if username + password match
        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {'error': 'Invalid username or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Valid login — start session
        login(request, user)

        # Get shop info for this user
        try:
            shop = user.shop
        except Shop.DoesNotExist:
            return Response(
                {'error': 'No shop linked to this account. Contact admin.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'message': f'Welcome! Logged into {shop.shop_name}',
            'shop_id': shop.id,
            'shop_name': shop.shop_name,
            'username': user.username,
        })


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})


class CurrentShopView(APIView):
    """
    React calls this on page load to check:
    "Is someone logged in? Which shop?"
    """
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Not logged in'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            shop = request.user.shop
            return Response({
                'shop_id': shop.id,
                'shop_name': shop.shop_name,
                'username': request.user.username,
                'gstin': shop.gstin,
                'mobile': shop.mobile,
                'address': shop.address,
            })
        except Shop.DoesNotExist:
            return Response({'error': 'No shop linked'}, status=400)