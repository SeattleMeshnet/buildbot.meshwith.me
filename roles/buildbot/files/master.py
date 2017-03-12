# -*- python -*-
# ex: set syntax=python:
import json
from buildbot.plugins import worker, schedulers, util, steps
from buildbot.util import identifiers
# from buildbot import statistics


with open('secrets.json') as f:
    secrets = json.load(f)

c = BuildmasterConfig = {}
c['workers'] = []
c['buildbotNetUsageData'] = 'full'

builders = {}

for w in secrets['workers']:
    hostname = identifiers.forceIdentifier(50, w['hostname'])
    if w['system'] not in builders:
        builders[w['system']] = {}
    for factory in w.get('factories', ['cjdns']):
        if factory not in builders[w['system']]:
            builders[w['system']][factory] = []
        builders[w['system']][factory].append(hostname)
    c['workers'].append(worker.Worker(hostname, w['password']))

c['protocols'] = {'pb': {'port': 9989}}


neonFlags = "-O2 -march=armv7-a -mtune=cortex-a8 -mfpu=neon -ftree-vectorize -ffast-math -mfloat-abi=hard -marm "\
            "-Wno-error=maybe-uninitialized"
windowsEnv = {"SYSTEM": "win32", "CROSS_COMPILE": "i686-w64-mingw32-"}

factories = {
    "cjdns": util.BuildFactory([steps.Git(repourl='git://github.com/cjdelisle/cjdns.git'),
                                steps.ShellCommand(command=['./clean'], name="Clean"),
                                steps.Compile(command=["./do"], env={"CTEST_OUTPUT_ON_FAILURE": "1"})]),
    "windows": util.BuildFactory([steps.Git(repourl='git://github.com/cjdelisle/cjdns.git'),
                                  steps.ShellCommand(command=['./clean']),
                                  steps.Compile(command=['./cross-do'], env=windowsEnv)]),
    "deb": util.BuildFactory([steps.Git(repourl='git://github.com/cjdelisle/cjdns.git'),
                              steps.ShellCommand(command=['./clean']),
                              steps.Compile(command=['dpkg-buildpackage'])]),
    "neon": util.BuildFactory([steps.Git(repourl='git://github.com/cjdelisle/cjdns.git'),
                               steps.ShellCommand(command=['./clean']),
                               steps.Compile(command=['./do'], env={"LDFLAGS": neonFlags, "CFLAGS": neonFlags}),
                               steps.ShellCommand(command=['./cjdroute', '--bench'])])
}

allBuilders = []

c['builders'] = []
for system in builders:
    for factory in builders[system]:
        name = system if factory == "cjdns" else "%s (%s)" % (system, factory)
        allBuilders.append(name)
        c['builders'].append(util.BuilderConfig(name=name, workernames=builders[system][factory],
                                                factory=factories[factory]))

c['schedulers'] = []
c['schedulers'].append(schedulers.AnyBranchScheduler(name="all", treeStableTimer=60, builderNames=allBuilders))
c['schedulers'].append(schedulers.ForceScheduler(name="force", builderNames=[str(x) for x in allBuilders]))

authz = util.Authz(allowRules=[
                util.StopBuildEndpointMatcher(role="admins"),
                util.ForceBuildEndpointMatcher(role="admins"),
                util.RebuildBuildEndpointMatcher(role="admins")
            ], roleMatchers=[util.RolesFromUsername(roles=["admins"], usernames=secrets['webauth'].keys())]
)
c['www'] = dict(port=8010,
                plugins=dict(waterfall_view={}, console_view={}),
                change_hook_dialects={'github': {}},
                auth=util.UserPasswordAuth(secrets['webauth'].iteritems()),
                authz=authz)

# hypeirc = words.IRC("fcf2:ff45:a10:2ca1:fb5c:426d:3505:4f18", "buildbot",
#                     channels=[{"channel": "#cjdns"}],
#                     notify_events={
#                         'exception': 1,
#                         'successToFailure': 1,
#                         'failureToSuccess': 1,
#                         'failure': 1
#                         }
#                     )
# c['status'].append(hypeirc)
# c['status'] = []
# irc = reporters.IRC("irc.fc00.io", "buildbot",
#                     useColors=False,
#                     channels=[{"channel": "#radar"}],
#                     notify_events={
#                         'started': 1,
#                         'success': 1,
#                         'failure': 1,
#                         'exception': 1
#                     })
# c['status'].append(irc)

c['title'] = "CJDNS"
c['titleURL'] = "https://github.com/cjdelisle/cjdns/"
c['buildbotURL'] = "https://buildbot.meshwith.me/cjdns/"
c['db_url'] = "sqlite:///state.sqlite"
