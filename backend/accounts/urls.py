from django.urls import path
from .views import LoginView, LogoutView, CurrentShopView

urlpatterns = [
    path('login/',   LoginView.as_view()),
    path('logout/',  LogoutView.as_view()),
    path('me/',      CurrentShopView.as_view()),
]