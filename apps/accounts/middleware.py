import time
from django.core.cache import cache
from django.http import JsonResponse
class TwoFactorMiddleware:
    WHITELIST = ("/accounts/", "/static/", "/media/", "/favicon")
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        u = getattr(request, "user", None)
        if (u is not None and getattr(u, "is_authenticated", False)
                and getattr(u, "role", "") in ("platform_admin", "school_admin")
                and getattr(u, "otp_secret", "")
                and not request.session.get("2fa_ok")
                and not request.path.startswith(self.WHITELIST)):
            from django.shortcuts import redirect
            return redirect("/accounts/2fa/")
        return self.get_response(request)
class RateLimitMiddleware:
    LIMIT = 60
    WINDOW = 60
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.method == "POST" and request.path.startswith("/api/"):
            u = getattr(request, "user", None)
            ident = str(getattr(u, "id", "")) or request.META.get("REMOTE_ADDR", "anon")
            key = "rl:%s:%d" % (ident, int(time.time() // self.WINDOW))
            try:
                current = cache.get(key)
                if current is None:
                    cache.set(key, 1, self.WINDOW)
                    count = 1
                else:
                    count = cache.incr(key)
            except Exception:
                count = 1
            if isinstance(count, int) and count > self.LIMIT:
                return JsonResponse({"detail": "Rate limit exceeded. Slow down."}, status=429)
        return self.get_response(request)
