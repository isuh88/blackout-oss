from django.urls import path

from users.views import UserSignupAPI, UserSigninAPI, UserRetrieveAPI

urlpatterns = [
    path('signup/', UserSignupAPI.as_view()),
    path('signin/', UserSigninAPI.as_view()),
    path('me/', UserRetrieveAPI.as_view()),
]