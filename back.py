#!/usr/bin/python3

import os
import pprint
import subprocess
import shlex
import sys

try:
    import yaml
except:
    print("No YAML")
    os.system('zypper in -y python3-PyYAML')
    import yaml

try:
    localCfgFile = 'cfg/' + sys.argv[1]
    tasksCfg = yaml.load(open(localCfgFile))
except:
    print(" !  Error reading tasks",localCfgFile)
    quit(1)

try:
    globalCfgFile='cfg/global.yaml'
    globalCfg = yaml.load(open(globalCfgFile))
    rdiff = globalCfg["global"]["rdiff"]
except:
    print(" !  Error reading global cfg",globalCfgFile)
    quit(1)
pprint.pprint(globalCfg)
pprint.pprint(tasksCfg)


for task in tasksCfg["tasks"]:
    if task.startswith('.'):
        continue

    purge = tasksCfg["tasks"][task][0]
    src = tasksCfg["tasks"][task][1]
    dst = tasksCfg["tasks"][task][2]

    r_schema=globalCfg['global']['remote-schema']

    pprint.pprint(purge)

    srcHostAndUserPart = ''
    if not src["src"]["host"] is None:
        srcHostAndUserPart = "%s@%s::" % (src["src"]["user"], src["src"]["host"])

    dstHostAndUserPart = ''
    if not dst["dst"]["host"] is None:
        dstHostAndUserPart = "%s@%s::" % (dst["dst"]["user"], dst["dst"]["host"])
    dstBase = os.path.normpath('/'.join([dst["dst"]["dir"], src["src"]["hostid"]]))

    if not (srcHostAndUserPart == "" and dstHostAndUserPart == ""):
        #remoteSchema = "  --remote-schema 'ssh  -C %s /opt/bin/rdiff-backup --server' "
        remoteSchema = r_schema
    else:
        remoteSchema = ""

    for srcDir in src["src"]["dirs"]:
        dstDir = os.path.normpath('/'.join([dstBase, srcDir]))
        lf = "%s[%s:%s]->[%s:%s].log" % (
            task, src["src"]["host"], srcDir.replace("/", "_"), dst["dst"]["host"], dstDir.replace("/", "_"))
        if os.path.exists(lf):
            os.remove(lf)

        if globalCfg["global"]["purge"]["do"] and purge["purge"]["do"]:
            if purge["purge"] is None:
                pperiod = globalCfg["global"]["purge"]["period"]
            else:
                pperiod = purge["purge"]["period"]
            # $cmdp="rdiff-backup --force --remove-older-than $srok --terminal-verbosity 5 --remote-schema 'ssh  -C %s rdiff-backup --server'  root\@10.10.0.95\:\:'/$prefix/$hostname/$i'";
            pcmd = "%s --force --remove-older-than %s --terminal-verbosity 5 %s %s'%s' " % (
                rdiff, pperiod, remoteSchema, dstHostAndUserPart, dstDir)
            print("----- Purge   ")
            print(pcmd)
            args = shlex.split(pcmd)

            p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0,
                                 universal_newlines=True)

            log=open('purge-'+lf,mode='w',encoding='utf8')
            while p.poll() is None:
                l = p.stderr.readline()
                print(l.strip("\n"))
                log.write(l)
                log.flush()
            log.close()

            print("===== end of purge ====")

        if os.path.exists('/opt/back/stop'):
            quit()


        bcmd = "%s %s --force --terminal-verbosity 5 --ssh-no-compression  --print-statistics --no-compare-inode --no-eas --parsable-output  --preserve-numerical-ids --create-full-path --exclude-device-files --exclude-fifos --exclude-sockets --exclude-symbolic-links" % (
            rdiff, remoteSchema)

        for excl in globalCfg["global"]["exclude"]:
            bcmd = bcmd + " --exclude '%s' " % excl

        bcmd = "%s -b %s'%s' %s'%s'" % (bcmd, srcHostAndUserPart, srcDir, dstHostAndUserPart, dstDir)
        print(bcmd)

        args = shlex.split(bcmd)
        p = subprocess.Popen(args,stderr=subprocess.PIPE,stdout=subprocess.PIPE,bufsize=0,universal_newlines=True)
        log = open('backup-' + lf, mode='w', encoding='utf8')

        while p.poll() is None:
            l=p.stderr.readline()
            print(l.strip("\n"))
            log.write(l)
            log.flush()
        log.close()


        print("===== end of backup ====")

        if os.path.exists('/opt/back/stop'):
            quit()
