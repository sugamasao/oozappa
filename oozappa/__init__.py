# -*- coding:utf8 -*-
import os
import sys
import subprocess
import logging
import json
from uuid import uuid4

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

version_info = (0, 9, 1)
__version__ = ".".join([str(v) for v in version_info])


class LogfileCommunicator(object):

    def __init__(self, logfile_base):
        self.logfile = os.path.join(
            logfile_base, '{0}.log'.format(uuid4().hex))

    def __enter__(self):
        self._f = open(self.logfile, 'w')
        return self

    def __exit__(self, type, value, traceback):
        self._f.close()

    def write(self, line):
        self._f.write('{0}'.format(line))
        logger.info(line)

    def controll(self, line):
        logger.info(line)


class LogWebsocketCommunicator(LogfileCommunicator):

    def __init__(self, websocket, logfile_base):
        super(LogWebsocketCommunicator, self).__init__(logfile_base)
        self.wsocket = websocket

    def write(self, line):
        super(LogWebsocketCommunicator, self).write(line)
        try:
            if self.wsocket:
                print(line)
                self.wsocket.send(json.dumps({'output': line}))
        except Exception, e:
            logger.warn(e)

    def controll(self, line):
        super(LogWebsocketCommunicator, self).controll(line)
        try:
            if self.wsocket:
                self.wsocket.send(json.dumps({'message_type': line}))
        except Exception, e:
            logger.warn(e)


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
