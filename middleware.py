from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    def __init__(self, app, requests_per_minute: int = 60):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.requests = {}

    async def __call__(self, request: Request, call_next):
        # Lấy IP của client
        client_ip = request.client.host
        
        # Kiểm tra rate limit
        current_time = time.time()
        if client_ip in self.requests:
            time_window = 60  # 1 phút
            client_requests = [t for t in self.requests[client_ip] if current_time - t < time_window]
            
            if len(client_requests) >= self.requests_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Please try again later."}
                )
            
            client_requests.append(current_time)
            self.requests[client_ip] = client_requests
        else:
            self.requests[client_ip] = [current_time]
        
        # Log request
        logger.info(f"{request.method} {request.url.path} - {client_ip}")
        
        response = await call_next(request)
        return response

# Thêm vào main.py sau khi tạo app
# from middleware import RateLimitMiddleware
# app.add_middleware(RateLimitMiddleware)