import os
import yaml
import time
import shutil
import subprocess

from json import dumps
from .base import Base


class Run(Base):
    def _read_config(self, filepath):
        with open(filepath, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data

    def _purge_mons(self):
        cmd = ["ceph-deploy", "mon", "destroy"]
        cmd.extend(self._config_dict["mon"])
        self._execute(cmd)

    def _install_ceph_deploy(self):
        if not os.path.exists("/tmp/ceph-deploy"):
            cmd = ["git", "clone", "https://github.com/JayjeetAtGithub/ceph-deploy", "/tmp/ceph-deploy"]
            self._execute(cmd)

        cmd = ["pip3", "install", "--upgrade", "/tmp/ceph-deploy"]
        self._execute(cmd)

    def _prepare_admin(self):
        shutil.rmtree(self._working_dir, ignore_errors=True)
        os.mkdir(self._working_dir)
        self._install_ceph_deploy()

    def _create_mons(self):
        self._purge_mons()
        time.sleep(5)

        cmd = ["ceph-deploy", "new"]
        cmd.extend(self._config_dict["mon"])
        self._execute(cmd, cwd=self._working_dir)

        cmd = ["ceph-deploy", "--overwrite-conf", "mon", "create-initial"]
        self._execute(cmd, cwd=self._working_dir)

        cmd = ["ceph-deploy", "admin"]
        cmd.extend(self._config_dict["mon"])
        self._execute(cmd, cwd=self._working_dir)

    def _copy_config(self):
        if self._is_dev():
            return
        shutil.copyfile(
            os.path.join(self._working_dir, 'ceph.conf'), '/etc/ceph/ceph.conf')

        shutil.copyfile(
            os.path.join(self._working_dir, 'ceph.client.admin.keyring'), '/etc/ceph/ceph.client.admin.keyring')

    def _install_daemons(self):
        cmd = ["ceph-deploy", "install", "--release", self._config_dict["version"]]
        servers = list()
        servers.extend(self._config_dict["osd"]["hosts"])
        servers.extend(self._config_dict["mon"])
        servers.extend(self._config_dict["mgr"])
        servers.extend(self._config_dict["mds"])
        cmd.extend(list(set(servers)))
        self._execute(cmd, cwd=self._working_dir)

    def _create_mgr(self):
        cmd = ["ceph-deploy", "mgr", "create"]
        cmd.extend(self._config_dict["mgr"])
        self._execute(cmd, cwd=self._working_dir)

    def _create_mds(self):
        pass

    def run(self):
        config_file_path = str(self.options['<config>'])
        _config_dict = self._read_config(config_file_path)
        self._config_dict = _config_dict
        self._prepare_admin()
        self._install_daemons()
        self._create_mons()
        self._copy_config()
        # self._create_mgr()
