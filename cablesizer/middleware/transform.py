from decimal import Decimal

from django.utils.deprecation import MiddlewareMixin


class DecimalToFloatInSession(MiddlewareMixin):
    def process_response(self, request, response):
        for key, value in request.session.items():
            if type(value) == Decimal:
                request.session[key] = float(request.session[key])
        return response