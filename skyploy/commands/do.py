import os
import yaml
import subprocess

from json import dumps
from .base import Base


class Do(Base):
    def _read_config(self, filepath):
        with open(filepath, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data

    def _purge_mons(self):
        cmd = ["ceph-deploy", "mon", "destroy"]
        cmd.extend(self._config_dict["mon"])
        self._execute(cmd)

    def _install_ceph_deploy(self):
        # check if ceph-deploy already cloned
        if not os.path.exists("/tmp/ceph-deploy"):
            cmd = ["git", "clone", "https://github.com/JayjeetAtGithub/ceph-deploy", "/tmp/ceph-deploy"]
            self._execute(cmd)

        cmd = ["pip3", "install", "--upgrade", "/tmp/ceph-deploy"]
        self._execute(cmd)

    def _prepare_admin(self):
        # install ceph-deploy
        self._install_ceph_deploy()
        # create the working directory
        os.makedirs(self._working_dir, exist_ok=True)

    def _create_mon(self):
        self._purge_mons()
        # deploy mons
        cmd = ["ceph-deploy", "new"]
        cmd.extend(self._config_dict["mon"])
        self._execute(cmd)

        with open("ceph.conf", 'a') as f:
            f.write(f"public_network = {self._config_dict['public_network']}")

        cmd = ["ceph-deploy", "--overwrite-conf", "mon", "create-initial"]
        self._execute(cmd)

        cmd = ["ceph-deploy", "admin"]
        cmd.extend(self._config_dict["mon"])
        self._execute(cmd)

    def _install_daemons(self):
        cmd = ["ceph-deploy", "install", "--release", self._config_dict["version"]]
        cmd.extend(self._config_dict["osd"]["hosts"])
        self._execute(cmd)

    def _create_mgr(self):
        cmd = ["ceph-deploy", "mgr", "create"]
        cmd.extend(self._config_dict["mgr"])
        self._execute(cmd)

    def _create_mds(self):
        pass

    def run(self):
        # change into the working dir
        config_file_path = str(self.options['<config>'])
        _config_dict = self._read_config(config_file_path)
        self._config_dict = _config_dict
        os.chdir(self._working_dir)
        self._prepare_admin()
        self._install_daemons()
        self._create_mon()
        # self._create_mgr()
