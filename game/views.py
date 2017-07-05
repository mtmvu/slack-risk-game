import os

from django.http import HttpResponse, HttpResponseForbidden
from django.views import View

from game.commands import Command


class Risk(View):

    def get(self, request):
        return HttpResponse('Hello!')

    def post(self, request):
        data = request.body
        if data.get('token', False) != os.environ.get('SLACK_COMMAND_TOKEN'):
            return HttpResponseForbidden()
        response = Command(data).read()
