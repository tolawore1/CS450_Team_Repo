from .base import Metric
from .score_available_dataset_and_code import AvailableDatasetAndCodeMetric
from .score_bus_factor import BusFactorMetric
from .score_code_quality import CodeQualityMetric
from .score_dataset_quality import DatasetQualityMetric
from .score_license import LicenseMetric
from .score_performance_claims import PerformanceClaimsMetric
from .score_ramp_up_time import RampUpMetric
from .score_size import SizeMetric

score_license = LicenseMetric().score
score_size = SizeMetric().score
score_ramp_up_time = RampUpMetric().score
score_bus_factor = BusFactorMetric().score
score_available_dataset_and_code = AvailableDatasetAndCodeMetric().score
score_dataset_quality = DatasetQualityMetric().score
score_code_quality = CodeQualityMetric().score
score_performance_claims = PerformanceClaimsMetric().score

__all__ = [
    "score_size",
    "score_license",
    "score_ramp_up_time",
    "score_bus_factor",
    "score_available_dataset_and_code",
    "score_dataset_quality",
    "score_code_quality",
    "score_performance_claims",
]
