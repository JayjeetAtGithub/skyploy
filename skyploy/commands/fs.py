import os
import yaml
import shutil
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
            f"{int(self._config_dict['fs']['data_pool_pg_count'])}"
        ]
        self._execute(cmd)

        cmd = [
            "ceph", "osd", "pool", "create", 
            self._config_dict["fs"]["metadata_pool"],
            f"{int(self._config_dict['fs']['metadata_pool_pg_count'])}"
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
        cmd = f"umount -uz {self._config_dict['fs']['path']}"
        self._execute(cmd.split())

        cmd = f"rm -rf {self._config_dict['fs']['path']}"
        self._execute(cmd.split())

        cmd = f"mkdir -p {self._config_dict['fs']['path']}"
        self._execute(cmd.split())

        cmd = f"ceph-fuse {self._config_dict['fs']['path']}"
        self._execute(cmd.split())

    def run(self):
        self._deploy_mds()
        self._deploy_cephfs()
        self._mount()
