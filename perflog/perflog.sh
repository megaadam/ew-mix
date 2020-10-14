#!/bin/bash

samplerate=10
sepflag=0

while [ 1 ]; do

    j8count=$(/bin/ps -elf | grep make |  grep  '\-j 8'  | wc -l)
    mpstat=$(mpstat -P all $samplerate 1 -o JSON)
    ps2=$(ps -e -o pcpu,comm,args --sort=-pcpu)
    #for entry in $ps2; do
        # echo ... $entry
    #done
    ps=$( ps -e -o pcpu,comm --sort=-pcpu | \
          awk  '{ORS=","; if ($1 > 9) print  "{cpu: " $1 ", proc: " $2 "}" }' | \
          sed 's/.$//' )

    docker=$(  docker ps |          awk  '{ORS=","; if ($1 > 1) print  "{ IMAGE: " $2 ", NAMES: " $11 "} \n"  }')

    if [ $sepflag = 1 ]; then
       echo ","
    fi
    sepflag=1
    echo {

    echo '    "date":      "'$(date)'"',
    echo '    "j8_count":  "'$j8count'"',
    echo '    "ps":        "['$ps']"',
    echo '    "mpstat":    '$mpstat,
    echo '    "docker":    '$docker

    echo }
    echo
done

