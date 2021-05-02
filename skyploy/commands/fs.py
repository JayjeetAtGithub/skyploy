import os
import yaml
import subprocess

from json import dumps
from .base import Base


class Fs(Base):
    def _deploy_mds(self):
        cmd = ["ceph-deploy", "mds", "create"]
        cmd.extend(self._config_dict["mds"])
        self._execute(cmd, cwd=self._working_dir)

    def _deploy_cephfs(self):
        cmd = [
            "ceph", "osd", "pool", "create", 
            self._config_dict["fs"]["data_pool"],
            int(self._config_dict["fs"]["data_pool_pg_count"])
        ]
        self._execute(cmd)

        cmd = [
            "ceph", "osd", "pool", "create", 
            self._config_dict["fs"]["metadata_pool"],
            int(self._config_dict["fs"]["metadata_pool_pg_count"]) 
        ]
        self._execute(cmd)

        cmd = [
            "ceph", "fs", "new",
            self._config_dict["fs"]["client_fs"],
            self._config_dict["fs"]["data_pool"],
            self._config_dict["fs"]["metadata_pool"]
        ]
        self._execute(cmd)

    def _mount(self):
        os.makedirs(self._config_dict["cephfs_mount_path"], exists_ok=True)
