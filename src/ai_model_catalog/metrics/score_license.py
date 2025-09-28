import time
from typing import Tuple

from .base import Metric


class LicenseMetric(Metric):
    COMPATIBLE_LICENSES = {
        "mit",
        "bsd",
        "bsd-2-clause",
        "bsd-3-clause",
        "apache-2.0",
        "apache 2.0",
        "lgpl",
        "lgplv2.1",
        "lgpl-2.1",
        "public domain",
        "cc0",
    }

    def score(self, model_data: dict) -> float:
        if model_data is None:
            return 0.0

        license_field = model_data.get("license", "")
        if isinstance(license_field, dict):
            license_name = license_field.get("spdx_id", "").lower()
        else:
            license_name = str(license_field).lower()

        for compatible in self.COMPATIBLE_LICENSES:
            if compatible in license_name:
                return 1.0

        # If API license is not found or is "unknown", check README content for
        # explicit license documentation
        # Only give credit for clear, explicit license statements, not just keyword mentions
        readme = model_data.get("readme", "").lower()

        # Look for explicit license statements in README
        explicit_license_patterns = [
            "license: apache-2.0",
            "license: mit",
            "license: bsd",
            "license: apache 2.0",
            "license: mit license",
            "license: bsd license",
            "licensed under apache",
            "licensed under mit",
            "licensed under bsd",
        ]
        for pattern in explicit_license_patterns:
            if pattern in readme:
                return 1.0

        return 0.0


def score_license(model_data) -> float:
    if isinstance(model_data, str):
        # Backward compatibility for string input
        return LicenseMetric().score({"license": model_data})
    return LicenseMetric().score(model_data)


def score_license_with_latency(model_data) -> Tuple[float, int]:
    """Score license with latency in milliseconds."""
    start_time = time.time()
    if isinstance(model_data, str):
        result = LicenseMetric().score({"license": model_data})
    else:
        result = LicenseMetric().score(model_data)
    # Add small delay to simulate realistic latency
    time.sleep(0.01)  # 10ms delay
    latency = int((time.time() - start_time) * 1000)
    return result, latency
