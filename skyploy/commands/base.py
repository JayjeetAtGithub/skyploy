import os
import sys
import subprocess
import logging


logging.basicConfig(level=logging.INFO)


class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def _check_not_ok(self, e, msg):
        if e != 0:
            logger.error(msg)
            sys.exit(e)

    def _execute(self, cmd, env=None, cwd=os.getcwd(), pids=set(), log=True):
        if os.environ['DEV']:
            logging.info(cmd)
            return 0, 0, ""
        
        pid = 0
        ecode = None
        try:
            with Popen(
                cmd,
                stdout=PIPE,
                stderr=STDOUT,
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

        except SubprocessError as ex:
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
