from django.utils.cache import add_never_cache_headers

class NoCacheMiddleware:
    """
    Middleware to ensure that authenticated pages are not cached by the browser.
    This prevents users from hitting the 'back' button after logout to view protected pages.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # We don't cache pages if the user is authenticated to avoid
        # showing logged-in pages when pressing 'Back' after logging out.
        if hasattr(request, 'user') and request.user.is_authenticated:
            add_never_cache_headers(response)
            
        return response
