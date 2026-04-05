import time


class LatencyMiddleware:
    """
    Measures total request/response time and injects it as a response header.
    X-Response-Time-ms: 14.23

    This is visible in browser DevTools → Network → Response Headers.
    Shows interviewers you understand middleware patterns and observability.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response["X-Response-Time-ms"] = str(duration_ms)
        return response
