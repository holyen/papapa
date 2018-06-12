#!/bin/bash

# "文件切割手术"工具
#由于爬虫下来的结果只按照分页进行目录存储，
#但每一页都会有100条左右的文件，使用起来不方便.
#故开发此工具将文件进行切割，并按照一定的目录名称创建目录
#例如 “1”目录下有29个文件，则会根据WEIGHT(10)的大小进行切割,切割成1-10，11-20，21-30,每个目录下有10，10，9个文件
# 切割前
# 1->>1,2,3,4...29.txt
# 切割后
# 1->>1-10->>1,2,3,4...10.txt
#  ->>11-20->>11,12,13...20.txt
#  ->>21-30->>21,22,23...29.txt



WORK_DIR=`pwd`
TORRENT_DIRS=$WORK_DIR/torrent

FILE_SPLIT_CHAR="-"

#切割条件
WEIGHT=10

split(){
	CURRENT_DIR=$1
	cd $CURRENT_DIR
	CURRENT_DIR_NAME=`pwd`
	# 子文件
	#目录下的文件数量大于最大数量,进行切割
	FILES_COUNT=`ls -l | grep "^-" | wc -l`
	if [[ $FILES_COUNT -gt $WEIGHT ]]; then
		# 大于WEIGHT
		#分组数(商)
		GROUPS_COUNT=$(($FILES_COUNT/$WEIGHT))
		#(多出来的部分)余数
		REMAINING_COUNT=$(($FILES_COUNT%$WEIGHT))
		#处理分组数
		for (( index = 1; index <= $GROUPS_COUNT; index++ )); do
			START=$(($(($(($index-1))*$WEIGHT))+1))
			END=$(($index*$WEIGHT))
			NEW_DIR_NAME=$START$FILE_SPLIT_CHAR$END
			if [ -d $NEW_DIR_NAME ]; then  
				# 读取最后一个文件夹并进行字符串分割
				prefix=`ls -l | grep "^d" | awk '{print $9}' |sort -n |tail -1 | cut -d $FILE_SPLIT_CHAR -f1 ` 
				suffix=`ls -l | grep "^d" | awk '{print $9}' |sort -n |tail -1 | cut -d $FILE_SPLIT_CHAR -f2 `
				START=$(($prefix+$WEIGHT))
				END=$(($suffix+$WEIGHT))
				echo "文件夹已经存在，自动寻找更名为...."$CURRENT_DIR_NAME/$START-$END
				NEW_DIR_NAME=$START$FILE_SPLIT_CHAR$END
			fi 
			mkdir "$NEW_DIR_NAME"  
			find $CURRENT_DIR_NAME -name "*.torrent" -maxdepth 1 | head -n $WEIGHT  | tail -n +1 | xargs -I '{}' mv {} $NEW_DIR_NAME
		done
		#处理多出来的部分
		if [[ $REMAINING_COUNT -gt 0 ]]; then
			prefix=`ls -l | grep "^d" | awk '{print $9}' |sort -n |tail -1 | cut -d $FILE_SPLIT_CHAR -f1 ` 
			suffix=`ls -l | grep "^d" | awk '{print $9}' |sort -n |tail -1 | cut -d $FILE_SPLIT_CHAR -f2 `
			START=$(($prefix+$WEIGHT))
			END=$(($suffix+$WEIGHT))
			NEW_DIR_NAME=$START$FILE_SPLIT_CHAR$END
			mkdir "$NEW_DIR_NAME"  
			find $CURRENT_DIR_NAME -name "*.torrent" -maxdepth 1 | head -n $WEIGHT  | tail -n +1 | xargs -I '{}' mv {} $NEW_DIR_NAME
		fi
	fi
	#子目录
	if [[ `ls -l | grep "^d" | wc -l` -gt 0 ]]; then
		for SUB_DIR in `ls  -l |grep "^d" |awk '{print $9}'`; do
			cd $SUB_DIR
			split ./
			cd ..
		done
	else 
		cd $CURRENT_DIR
	fi
}

split $TORRENT_DIRS
cd $WORK_DIR
./repeat.sh