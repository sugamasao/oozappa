# -*- coding:utf8 -*-
import os
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

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
