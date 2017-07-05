import os

from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views import View

from game.commands import Command
from game.commands import ValidationException


class Risk(View):

    def get(self, request):
        return HttpResponse('Hello!')

    def post(self, request):
        data = request.body
        if data.get('token', False) != os.environ.get('SLACK_COMMAND_TOKEN'):
            return HttpResponseForbidden()
        try:
            response = Command(data).execute()
        except ValidationException as e:
            data = {"response_type": "ephemeral",
                    "text": str(e)}

        return JsonResponse(data)
