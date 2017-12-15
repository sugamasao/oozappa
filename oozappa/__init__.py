# -*- coding:utf8 -*-
import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

version_info = (0, 9, 0)
__version__ = ".".join([str(v) for v in version_info])

class exec_fabric(object):

    PROGRESS_BEGIN = 2
    EXEC_SUCESSFUL = 3
    EXEC_FAILED = 4

    def __init__(self, path, cli=False):
        self.cli = cli
        self.initial_path = os.getcwd()  # TODO
        if not os.path.isabs(path):
            self.exec_path = os.path.join(self.initial_path, path)
        else:
            self.exec_path = path
        self.path_appended = False

    def __enter__(self):
        os.chdir(self.exec_path)
        if not (self.exec_path in sys.path):
            sys.path.insert(0, self.exec_path)
            self.path_appended = True
        return self

    def __exit__(self, type, value, traceback):
        os.chdir(self.initial_path)
        if self.path_appended:
            sys.path.remove(self.exec_path)

    def doit(self, fabric_commands=[], communicator=None):
        execute_commands = '<<doit: fab {0}>>\n'.format(
            ' '.join(fabric_commands))
        logger.debug(execute_commands)
        communicator.write(execute_commands)
        p = subprocess.Popen(["fab"] + fabric_commands,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             universal_newlines=True)
        stderr = p.stdout
        while True:
            line = stderr.readline()
            if not line:
                break
            communicator.write(line)
        return p.wait()
