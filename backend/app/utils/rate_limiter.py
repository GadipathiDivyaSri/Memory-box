"""
MemoryBox Rate Limiter Utility
Initializes SlowAPI Limiter to prevent brute force and DDoS attacks on critical endpoints.
"""

import os
import sys
from slowapi import Limiter
from slowapi.util import get_remote_address

is_test_env = os.getenv("TESTING", "").lower() in ("1", "true", "yes") or "pytest" in sys.modules

# Initialize standard IP-based rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    enabled=not is_test_env
)

# Export standard auth rate limiter decorator (5 requests per minute)
auth_rate_limit = limiter.limit("5/minute")
