import os
import yaml
import subprocess

from json import dumps
from .base import Base


class Grafana(Base):
    def _start_prometheus(self):
        cmd = ["docker", "rm", "skyhook-prometheus", "--force"]
        self._execute(cmd)

        cmd = ["docker", "pull", "prom/prometheus"]
        _, e, _ = self._execute(cmd)
        self._check_not_ok(e, "failed to pull prom/prometheus image")
        
        cmd = ["docker", "run", "-d", "-p", "9090:9090", "--name", "skyhook-prometheus", "prom/prometheus"]
        _, e, _ = self._execute(cmd)
        self._check_not_ok(e, "failed to start prometheus container")

    def _start_grafana(self):
        cmd = ["docker", "rm", "skyhook-grafana", "--force"]
        self._execute(cmd)
        
        cmd = ["docker", "pull", "grafana/grafana"]
        _, e, _ = self._execute(cmd)
        self._check_not_ok(e, "failed to pull grafana/grafana image")

        cmd = ["docker", "run", "-d", "-p", "3000:3000", "--name", "skyhook-grafana", "grafana/grafana"]
        _, e, _ = self._execute(cmd)
        self._check_not_ok(e, "failed to start grafana container")

    def run(self):
        self._is_installed('docker')
        self._start_prometheus()
        self._start_grafana()
