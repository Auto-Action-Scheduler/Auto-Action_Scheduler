from rest_framework.renderers import JSONRenderer
from django.conf import settings as app_settings

STATUS = app_settings.STATUS_CODES


class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):

        status_code = renderer_context["response"].status_code
        response = {
            "status": STATUS['success'],
            "data": data,
            "message": "Successfully Retrieved"
        }

        if not str(status_code).startswith("2"):
            response["status"] = STATUS['error']
            response["data"] = None
            try:
                response["message"] = "something went wrong, trying to perform this action"
                response["error"] = data
            except KeyError:
                response['data'] = ''

        return super(CustomRenderer, self).render(response, accepted_media_type, renderer_context)
