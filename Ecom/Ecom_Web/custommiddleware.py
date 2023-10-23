from django.shortcuts import redirect

class CheckoutRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'GET':
            # Store the current page URL in the session
            request.session['current_url'] = request.build_absolute_uri()
            request.session['previous_url'] = request.META.get('HTTP_REFERER' , None)

        response = self.get_response(request)


        return response