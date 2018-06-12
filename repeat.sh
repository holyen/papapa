#!/bin/bash

##将重复的文件进行删除，并清理空目录

WORK_DIR=`pwd`
TORRENT_DIRS=$WORK_DIR/torrent

#查重
echo "执行repeat.sh"
a=0
for torrent_repeat_file in `ls -lR $TORRENT_DIRS |grep "^-" |awk '{print $9}' | sort | uniq -c | grep -v " 1 " | awk '{print $2}'`; do
	# if [[ $a -eq 1 ]]; then
		echo $torrent_repeat_file
		find $TORRENT_DIRS -name $torrent_repeat_file -type f |awk 'NR>1' |xargs rm   
	# fi
	# let a++
done

#清理空目录
find $TORRENT_DIRS -type d -empty | xargs -n 1 rm -rf