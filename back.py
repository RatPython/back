#!/usr/bin/python3

import os
import pprint
import subprocess
import shlex
import sys

try:
    import yaml
except:
    print ("No YAML")
    os.system('zypper in -y python3-PyYAML')
    import yaml


localCfgFile='cfg/'+sys.argv[1]
print(localCfgFile)
globalCfg=yaml.load(open('cfg/global.yaml'))
tasksCfg=yaml.load(open(localCfgFile))

rdiff=globalCfg["global"]["rdiff"]

pprint.pprint(globalCfg)
pprint.pprint(tasksCfg)
for task in tasksCfg["tasks"]:
    if task.startswith('.'):
       continue

    purge=tasksCfg["tasks"][task][0]
    src=tasksCfg["tasks"][task][1]
    dst=tasksCfg["tasks"][task][2]
    pprint.pprint(purge)


    srcHostAndUserPart=''
    if not src["src"]["host"] is None:
       srcHostAndUserPart="%s@%s::" % (src["src"]["user"],src["src"]["host"])

    dstHostAndUserPart=''
    if not dst["dst"]["host"] is None:
       dstHostAndUserPart="%s@%s::" % (dst["dst"]["user"],dst["dst"]["host"])
    dstBase=os.path.normpath('/'.join([dst["dst"]["dir"],src["src"]["hostid"]]))

    if not (srcHostAndUserPart=="" and dstHostAndUserPart==""):
       remoteSchema="  --remote-schema 'ssh  -C %s /opt/bin/rdiff-backup --server' "
    else:
       remoteSchema=""

    for srcDir in src["src"]["dirs"]:
       dstDir=os.path.normpath('/'.join([dstBase,srcDir]))
       lf="%s[%s:%s]->[%s:%s].log" % (task,src["src"]["host"],srcDir.replace("/","_"),dst["dst"]["host"],dstDir.replace("/","_"))
       if os.path.exists(lf):
          os.remove(lf)

#       print(srcPoint,dstPoint)

       if globalCfg["global"]["purge"]["do"] and purge["purge"]["do"]:
          if purge["purge"] is None:
               pperiod=globalCfg["global"]["purge"]["period"]
          else:
               pperiod=purge["purge"]["period"]
          #$cmdp="rdiff-backup --force --remove-older-than $srok --terminal-verbosity 5 --remote-schema 'ssh  -C %s rdiff-backup --server'  root\@10.10.0.95\:\:'/$prefix/$hostname/$i'";
          pcmd="%s --force --remove-older-than %s --terminal-verbosity 5 %s %s'%s'" % (rdiff,pperiod,remoteSchema,dstHostAndUserPart,dstDir)
          print("----- Purge   ")
          print(pcmd)
          args=shlex.split(pcmd)
          p=subprocess.Popen(args,stdout=open("purge-"+lf,'a+'),stderr=open("purge-"+lf,'a+'),universal_newlines=True,bufsize=0)
          p.wait()
          print("===== end of purge ====")
          #continue

       bcmd="%s %s --force --terminal-verbosity 5 --ssh-no-compression  --print-statistics --no-compare-inode --no-eas --parsable-output  --preserve-numerical-ids --create-full-path --exclude-device-files --exclude-fifos --exclude-sockets --exclude-symbolic-links" % (rdiff,remoteSchema)

       for excl in globalCfg["global"]["exclude"]:
          bcmd=bcmd+" --exclude '%s' " % excl

       bcmd="%s -b %s'%s' %s'%s'" % (bcmd,srcHostAndUserPart,srcDir,dstHostAndUserPart,dstDir)
       print (bcmd)
#       quit()
       args=shlex.split(bcmd)
       p=subprocess.Popen(args,stdout=open("backup-"+lf,'a+'),stderr=open("backup-"+lf,'a+'),universal_newlines=True,bufsize=0)
       p.wait()
       print("===== end of backup ====")
       if os.path.exists('/opt/back/stop'):
           break;


#    sendc="./sendm.py '%s'" % lf
#    args=shlex.split(sendc)
#    p=subprocess.Popen(args)
#    p.wait()
