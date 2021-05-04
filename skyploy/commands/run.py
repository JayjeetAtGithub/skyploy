import os
import time
import shutil
import subprocess

from json import dumps
from .base import Base


class Run(Base):
    def _cleanup(self):
        cluster_nodes = list()
        cluster_nodes.extend(self._config_dict["mon"])
        cluster_nodes.extend(self._config_dict["mgr"])
        cluster_nodes.extend(self._config_dict["mds"])
        cluster_nodes.extend(self._config_dict["osd"]["hosts"])
        cluster_nodes = list(set(cluster_nodes))

        cmd = ["ceph-deploy", "purge"]
        cmd.extend(cluster_nodes)
        _, e, _ = self._execute(cmd, cwd=self._working_dir)
        self._check_not_ok(e, "purge the existing ceph cluster")

    def _install_ceph_deploy(self):
        if not os.path.exists("/tmp/ceph-deploy"):
            cmd = ["git", "clone", "https://github.com/JayjeetAtGithub/ceph-deploy", "/tmp/ceph-deploy"]
            self._execute(cmd)

        cmd = ["pip3", "install", "--upgrade", "/tmp/ceph-deploy"]
        _, e, _ = self._execute(cmd)
        self._check_not_ok(e, "failed to install ceph-deploy")

    def _prepare_admin(self):
        if not self._is_dev():
            shutil.rmtree(self._working_dir, ignore_errors=True)
            os.makedirs(self._working_dir)
        self._install_ceph_deploy()

    def _copy_config(self):
        if self._is_dev():
            return
        cmd = ["apt", "install", "-y", "ceph-common", "ceph-fuse"]
        _, e, _ = self._execute(cmd)
        self._check_not_ok(e, "failed to install the ceph-common package")

        shutil.copyfile(
            os.path.join(self._working_dir, 'ceph.conf'), '/etc/ceph/ceph.conf')

        shutil.copyfile(
            os.path.join(self._working_dir, 'ceph.client.admin.keyring'), '/etc/ceph/ceph.client.admin.keyring')

    def _create_osds(self):
        osd_nodes = self._config_dict["osd"]["hosts"]
        for node in osd_nodes:
            cmd = f"ceph-deploy osd create  --data {self._config_dict['osd']['conf']['disk']} {node}"
            _, e, _ = self._execute(cmd.split(), cwd=self._working_dir)
            self._check_not_ok(e, "failed to create osd")

    def _create_mons(self):
        cmd = ["ceph-deploy", "mon", "destroy"]
        cmd.extend(self._config_dict["mon"])
        _, e, _ = self._execute(cmd, cwd=self._working_dir)
        
        time.sleep(5)

        cmd = ["ceph-deploy", "new"]
        cmd.extend(self._config_dict["mon"])
        _, e, _ = self._execute(cmd, cwd=self._working_dir)
        self._check_not_ok(e, "ceph-deploy new command failed")

        cmd = ["ceph-deploy", "--overwrite-conf", "mon", "create-initial"]
        _, e, _ = self._execute(cmd, cwd=self._working_dir)
        self._check_not_ok(e, "ceph-deploy mon create initial command failed")

        cmd = ["ceph-deploy", "admin"]
        cmd.extend(self._config_dict["mon"])
        _, e, _ = self._execute(cmd, cwd=self._working_dir)
        self._check_not_ok(e, "ceph-deploy admin command failed")

    def _install_daemons(self):
        cmd = ["ceph-deploy", "install", "--release", self._config_dict["version"]]
        servers = list()
        servers.extend(self._config_dict["osd"]["hosts"])
        servers.extend(self._config_dict["mon"])
        servers.extend(self._config_dict["mgr"])
        servers.extend(self._config_dict["mds"])
        cmd.extend(list(set(servers)))
        _, e, _ = self._execute(cmd, cwd=self._working_dir)
        self._check_not_ok(e, "failed to install ceph daemons")

    def _create_mgr(self):
        cmd = ["ceph-deploy", "mgr", "create"]
        cmd.extend(self._config_dict["mgr"])
        _, e, _ = self._execute(cmd, cwd=self._working_dir)
        self._check_not_ok(e, "failed to create mgrs")

    def run(self):
        self._cleanup()
        self._prepare_admin()
        self._install_daemons()
        self._create_mons()
        self._copy_config()
        self._create_mgr()
        self._create_osds()
