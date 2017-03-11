import os
import sys
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.application import service

from buildbot.master import BuildMaster

basedir = os.path.abspath(os.path.dirname(__file__))
configfile = 'master.py'

application = service.Application('buildmaster')
application.setComponent(ILogObserver, FileLogObserver(sys.stdout).emit)

m = BuildMaster(basedir, configfile, umask=None)
m.setServiceParent(application)
