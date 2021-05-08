#!/bin/bash -x




target=synology:yama
busy=/opt/back/busy.flag
mount_flag=/mnt/iscsi/iscsi-mounted
#in_progress=/mnt/iscsi/backup-in-progress

cd /opt/back

if [ -f $busy  ]; then
    echo "Busy flag!!\n"
    exit
fi

today=`date '+%Y-%m-%d__%H.%M.%S'`;
echo "Today is: [$today]"

echo "Set busy flag: [$busy]"
echo "1" > $busy

echo "Microtik config.."
cd mikrotik
./export-mikrotik.sh
cd /opt/back
call ./pg_dump.sh

#./copy-book.sh

./back.py nas.yaml > nas.log

#./back.py tank.yaml >> nas.log



tarlog="logs-$today.tar"

#rm log/c-veter/*.log
#cp *.log log/c-veter


tar -cf $tarlog *.log
xz -9 $tarlog

xzlog="$tarlog.xz"

mv $xzlog log

rm *.log


noshut=/opt/back/nas.nodown

rm $busy

#if [ -f $flag  ]; then
#    echo "Busy flag!!\n"
#    exit
#fi

#echo "1" > busy-nas.flag


#ssh 10.10.0.100 -t 'poweroff'
#if [ ! -f $noshut  ]; then
 
# ssh 10.10.0.100 -t 'nohup /opt/back/backup.sh' &
# ssh 10.10.0.100 -t 'poweroff'
 
 
#fi

#ssh 10.10.0.100 -t 'poweroff'


#umount /mnt/usb
#if [ -f /mnt/usb/usb-mounted ]; then
#    echo "ERRROR!! Can't unmount /dev/sde1 \n\n"
#fi



#./backup-disk