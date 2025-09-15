from ai_model_catalog.metrics.base import Metric

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
        license_field = model_data.get("license", "")
        if isinstance(license_field, dict):
            license_name = license_field.get("spdx_id", "").lower()
        else:
            license_name = str(license_field).lower()
        for compatible in self.COMPATIBLE_LICENSES:
            if compatible in license_name:
                return 1.0

        if license_name:
            return 0.0