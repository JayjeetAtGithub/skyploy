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

    def _install_ceph_deploy(self):
        # check if ceph-deploy already cloned
        if not os.path.exists("/tmp/ceph-deploy"):
            cmd = ["git", "clone", "https://github.com/ceph/ceph-deploy", "/tmp/ceph-deploy"]
            self._execute(cmd)

        cmd = ["pip3", "install", "--upgrade", "/tmp/ceph-deploy"]
        self._execute(cmd)

    def _prepare_admin(self):
        # install ceph-deploy
        self._install_ceph_deploy()

        # create the working directory
        self._working_dir = os.path.join(os.environ["HOME"], ".skyploy", "deployment")
        os.makedirs(self._working_dir, exist_ok=True)

    def _create_mon(self):
        # change into the working dir
        os.chdir(self._working_dir)

        # deploy mons
        cmd = ["ceph-deploy", "new"]
        cmd.extend(self.config_dict["mon"])
        print(cmd)
        self._execute(cmd)

        cmd = ["ceph-deploy", "mon", "create-initial"]
        print(cmd)
        self._execute(cmd)

        cmd = ["ceph-deploy", "admin"]
        cmd.extend(self.config_dict["mon"])
        print(cmd)
        self._execute(cmd)

    def _install_daemons(self):
        # change into the working dir
        os.chdir(self._working_dir)

        cmd = ["ceph-deploy", "install", "--release", self.config_dict["version"]]
        cmd.extend(self.config_dict["osd"]["hosts"])
        print(cmd)
        self._execute(cmd)

    def _create_mgr(self):
        # change into the working dir
        os.chdir(self._working_dir)

        cmd = ["ceph-deploy", "mgr", "create"]
        cmd.extend(self.config_dict["mgr"])
        print(cmd)
        self._execute(cmd)

    def _create_mds(self):
        pass

    def run(self):
        config_file_path = str(self.options['<config>'])
        config_dict = self._read_config(config_file_path)
        self.config_dict = config_dict
        print(self.config_dict)
        self._prepare_admin()
        self._install_daemons()
        self._create_mon()
        self._create_mgr()
