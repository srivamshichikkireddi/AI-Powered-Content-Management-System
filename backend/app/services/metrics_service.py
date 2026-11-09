from collections import defaultdict
from datetime import datetime, timezone
import time
from typing import Any, Dict, List


class MetricsCollector:
    """
    In-memory metrics collector exporting Prometheus metrics and administrative summaries
    (AICMS-F-022, AICMS-NF-002, AICMS-NF-005, TC-OPS-02, TC-OPS-03).
    """

    def __init__(self):
        self.start_time = time.time()
        self.request_counts = defaultdict(int)  # (method, path, status_code) -> count
        self.search_latencies: List[float] = []
        self.upload_success_count = 0
        self.upload_failure_count = 0
        self.total_requests = 0
        self.status_counts = defaultdict(int)  # 200, 400, 404, 500, etc.

    def record_request(self, method: str, path: str, status_code: int, duration_sec: float):
        self.total_requests += 1
        self.status_counts[status_code] += 1
        # Normalize path to avoid high cardinality
        normalized_path = path
        if path.startswith("/api/v1/documents/") and len(path.split("/")) > 4:
            normalized_path = "/api/v1/documents/{id}/" + "/".join(path.split("/")[4:])
        elif path.startswith("/api/v1/documents/") and len(path.split("/")) == 4:
            normalized_path = "/api/v1/documents/{id}"
        elif path.startswith("/api/v1/categories/") and len(path.split("/")) == 4:
            normalized_path = "/api/v1/categories/{id}"

        self.request_counts[(method, normalized_path, status_code)] += 1

        if "/api/v1/search" in path:
            self.search_latencies.append(duration_sec * 1000.0)  # ms

        if "/api/v1/documents/upload" in path:
            if 200 <= status_code < 300:
                self.upload_success_count += 1
            else:
                self.upload_failure_count += 1

    def get_uptime_seconds(self) -> float:
        return round(time.time() - self.start_time, 2)

    def get_availability_percentage(self) -> float:
        """
        Calculate system availability (AICMS-NF-002, TC-OPS-03).
        Target: >= 99.5% availability excluding scheduled downtime.
        """
        if self.total_requests == 0:
            return 100.0
        server_errors = sum(v for k, v in self.status_counts.items() if k >= 500)
        availability = max(0.0, (1.0 - (server_errors / self.total_requests))) * 100.0
        return round(availability, 2)

    def get_summary(self) -> Dict[str, Any]:
        """
        Produce administrative summary without leaking sensitive document content (AICMS-F-022, TC-OPS-02).
        """
        uptime = self.get_uptime_seconds()
        availability = self.get_availability_percentage()
        sorted_latencies = sorted(self.search_latencies) if self.search_latencies else [0.0]
        p50 = sorted_latencies[len(sorted_latencies) // 2]
        p90_idx = int(len(sorted_latencies) * 0.9)
        p90 = sorted_latencies[min(p90_idx, len(sorted_latencies) - 1)]

        return {
            "uptime_seconds": uptime,
            "availability_percentage": availability,
            "total_requests": self.total_requests,
            "uploads": {
                "total": self.upload_success_count + self.upload_failure_count,
                "successful": self.upload_success_count,
                "failed": self.upload_failure_count,
            },
            "search": {
                "total_queries": len(self.search_latencies),
                "median_latency_ms": round(p50, 2),
                "p90_latency_ms": round(p90, 2),
            },
            "status_code_distribution": {str(k): v for k, v in self.status_counts.items()},
        }

    def to_prometheus_format(self) -> str:
        """
        Generate standard Prometheus metrics text exposition.
        """
        lines = [
            "# HELP aicms_service_uptime_seconds Service uptime in seconds",
            "# TYPE aicms_service_uptime_seconds gauge",
            f"aicms_service_uptime_seconds {self.get_uptime_seconds()}",
            "",
            "# HELP aicms_availability_ratio Service availability ratio between 0.0 and 1.0",
            "# TYPE aicms_availability_ratio gauge",
            f"aicms_availability_ratio {self.get_availability_percentage() / 100.0:.4f}",
            "",
            "# HELP aicms_http_requests_total Total number of HTTP requests processed",
            "# TYPE aicms_http_requests_total counter",
        ]

        if not self.request_counts:
            lines.append('aicms_http_requests_total{method="GET",handler="/health",status="200"} 0')
        else:
            for (method, path, status_code), count in self.request_counts.items():
                lines.append(f'aicms_http_requests_total{{method="{method}",handler="{path}",status="{status_code}"}} {count}')

        lines.extend([
            "",
            "# HELP aicms_upload_operations_total Total upload operations",
            "# TYPE aicms_upload_operations_total counter",
            f'aicms_upload_operations_total{{outcome="success"}} {self.upload_success_count}',
            f'aicms_upload_operations_total{{outcome="failure"}} {self.upload_failure_count}',
        ])

        return "\n".join(lines) + "\n"


metrics_collector = MetricsCollector()
