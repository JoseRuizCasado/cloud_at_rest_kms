from django.shortcuts import render
from rest_framework import views, response, status


# Create your views here.
class api_say_hello(views.APIView):

    @staticmethod
    def get(request):
        """
        Simple example of API endpoint
        :param request: HTTP request
        :return: JSON with HELLO WORLD
        """
        # data is JSON with information to transmit in Response
        # status is HTTP request status
        return response.Response(data={'Hi': 'Hello World'}, status=status.HTTP_200_OK)
