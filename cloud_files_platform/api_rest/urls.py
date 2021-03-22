from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *

urlpatterns = [
    path('', api_say_hello.as_view(), name='hello'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
