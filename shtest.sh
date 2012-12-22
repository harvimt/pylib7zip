#!/bin/sh
#bourne shell implementation of the test program, similar to pytest.py sub (which uses sub_lib7zip.py)

#shell is used on the off-chance that pipes are implemented more efficiently in shell than in Python.
#in order to keep performance good, shell builtins should be preferred in all cases to external commands that would require forking

BASE_PATH="/media/Media/Games/Game Mods/oblivion/Bash Installers";

for file in "${BASE_PATH}"/*; do
	if [ -f "$file" ]; then
		echo "$file"
		i=0;
		started=0
		7za l -slt "$file" | \
		while read line; do

			if [ $started -eq 0 ]; then
				if echo -n "$line" | grep -E -q '^-{10}$'; then
					#[ $line = '----------' ] doesn't work because - is interpreted as a flag, couldn't find a way to escape it
					#this single grep shouldn't hurt perf too much since it's only run a handful of times per file (not every line)
					started=1;
				fi
				continue;
			fi

			case "$line" in
				'Path = '*)
					#ze_path=`echo $line | cut -c 7-`;
					ze_path=${line#'Path = '*}
					;;
				'CRC = '*)
					#ze_crc=`echo $line | cut -c 6-`;
					ze_crc=${line#'CRC = '*}
					if [ -z "$ze_crc" ]; then ze_crc='DEADBEEF'; fi
					;;
				'Attributes = .'*)
					ze_isdir='F'
					;;
				'Attributes = D'*)
					ze_isdir='D';
					;;
				'')
					#printf '%04d  %s  %s  %s\n' $i $ze_isdir $ze_crc "$ze_path";
					i=$((i+1));
				;;

			esac
		done
	fi
done
