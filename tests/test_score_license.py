import pytest

from ai_model_catalog.metrics.score_license import LicenseMetric, score_license


@pytest.mark.parametrize(
    "license_str",
    [
        "MIT",
        "mit",
        "Apache-2.0",
        "Apache 2.0",
        "BSD-3-Clause",
        "BSD-2-Clause",
        "LGPL",
        "LGPL-2.1",
        "LGPLv2.1",
        "Public Domain",
        "CC0-1.0",
        " cc0 ",  # whitespace ok
    ],
)
def test_compatible_strings_score_as_one(license_str):
    assert score_license(license_str) == 1.0
    assert LicenseMetric().score({"license": license_str}) == 1.0


def test_dict_spdx_id_supported():
    assert LicenseMetric().score({"license": {"spdx_id": "Apache-2.0"}}) == 1.0
    assert LicenseMetric().score({"license": {"spdx_id": "BSD-2-Clause"}}) == 1.0


@pytest.mark.parametrize("license_str", ["GPL-3.0", "Proprietary", "", None])
def test_incompatible_or_missing_scores_zero(license_str):
    assert score_license(license_str) == 0.0  # wrapper path
    assert LicenseMetric().score({"license": license_str}) == 0.0  # class path


def test_dict_missing_spdx_scores_zero():
    assert LicenseMetric().score({"license": {"name": "Custom"}}) == 0.0
