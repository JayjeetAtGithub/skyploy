import os
import sys
import subprocess
import logging

import yaml

from distutils.spawn import find_executable


logging.basicConfig(level=logging.INFO)


class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs
        self._working_dir = os.path.join(os.environ["HOME"], ".skyploy", "deployment")
        self._config_dict = self._read_config()

    def _read_config(self, filepath=".skyploy.yaml"):
        with open(filepath, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data

    def _is_installed(self, name):
        return find_executable(name) is not None

    def _check_not_ok(self, e, msg):
        if e != 0:
            logging.error(msg)
            sys.exit(e)

    def _is_dev(self):
        return os.environ.get("DEV", None)

    def _exit(self, msg):
        logging.error(msg)
        sys.exit(1)

    def _execute(self, cmd, env=None, cwd=os.getcwd(), pids=set(), log=True):
        if self._is_dev():
            logging.info(cmd)
            return 0, 0, ""

        pid = 0
        ecode = None
        try:
            with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                preexec_fn=os.setsid,
                env=env,
                cwd=cwd,
            ) as p:
                pid = p.pid
                pids.add(p.pid)

                output = []
                for line in iter(p.stdout.readline, ""):
                    if log:
                        logging.info(line.rstrip())
                    else:
                        output.append(line.rstrip())

                p.wait()
                ecode = p.poll()

            logging.debug(f"Code returned by process: {ecode}")

        except subprocess.SubprocessError as ex:
            output = ""
            if not ecode:
                ecode = 1
            logging.info(f"Command '{cmd[0]}' failed with: {ex}")
        except Exception as ex:
            output = ""
            ecode = 1
            logging.info(f"Command raised non-SubprocessError error: {ex}")

        return pid, ecode, "\n".join(output)

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')
