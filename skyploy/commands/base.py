import subprocess
import logging

class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs
    
    def _execute(self, cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            logging.info(line.rstrip())

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')
