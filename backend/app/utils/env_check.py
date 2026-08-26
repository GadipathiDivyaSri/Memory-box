"""
MemoryBox Environment Variable Validation Utility
Validates all required and optional environment configuration on backend startup.
"""

import os
import sys
import logging
from typing import Dict, List, Any

logger = logging.getLogger("memorybox.env_check")

# Definition of environment variables with criticality levels
REQUIRED_VARS: List[str] = [
    "JWT_SECRET_KEY",
]

RECOMMENDED_VARS: Dict[str, str] = {
    "GOOGLE_API_KEY": "Required for live Gemini 1.5 Flash generative AI understanding",
    "ENVIRONMENT": "Target deployment environment (development / staging / production)",
    "GOOGLE_CLOUD_PROJECT": "Target Google Cloud Project ID for Cloud Firestore/Storage",
}


def validate_environment() -> Dict[str, Any]:
    """
    Validates all critical environment variables on startup.
    Returns structured status dictionary.
    """
    missing_required: List[str] = []
    warnings: List[str] = []
    configured_vars: List[str] = []

    # 1. Check strict required variables
    for var in REQUIRED_VARS:
        val = os.getenv(var)
        if not val:
            # Check if default is present in settings
            from ..config import get_settings
            s = get_settings()
            if not getattr(s, var, None):
                missing_required.append(var)
            else:
                configured_vars.append(f"{var} (default)")
        else:
            configured_vars.append(var)

    # 2. Check recommended variables
    for var, purpose in RECOMMENDED_VARS.items():
        val = os.getenv(var)
        if not val:
            warnings.append(f"Recommended variable '{var}' not set in environment ({purpose}). Heuristic fallback active.")
        else:
            configured_vars.append(var)

    is_valid = len(missing_required) == 0

    if not is_valid:
        logger.error(f"[SECURITY ALERT] Missing required environment variables: {', '.join(missing_required)}")
    else:
        logger.info(f"[ENV CHECK] Environment configuration verified. Configured: {', '.join(configured_vars)}")
        for warn in warnings:
            logger.info(f"[ENV NOTICE] {warn}")

    return {
        "status": "ok" if is_valid else "error",
        "is_valid": is_valid,
        "missing_required": missing_required,
        "warnings": warnings,
        "configured_count": len(configured_vars)
    }


# Execute check if run directly as module
if __name__ == "__main__":
    res = validate_environment()
    print(f"Env Check Result: {res['status']}")
    if res["warnings"]:
        for w in res["warnings"]:
            print(f"  - {w}")
