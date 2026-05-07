from django.utils.cache import add_never_cache_headers, patch_vary_headers

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Apply no-cache headers to ALL responses so that no page
        # (including authenticated portal pages) is ever cached by the browser.
        # This prevents the "back button after logout" security issue where
        # a cached dashboard page could be shown to an unauthenticated user.
        add_never_cache_headers(response)
        # Vary on Cookie so the browser treats authenticated vs unauthenticated
        # versions of the same URL as different resources
        patch_vary_headers(response, ('Cookie',))
        return response
