from . import utils
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import api_view


# Create your views here.
@api_view(["POST"])
def cnn_response(request):
    url = request.data.get("url_to_check")
    result = utils.predict(url)
    return Response({"result": result}, status=HTTP_200_OK)
