#!/bin/bash
#
# Author Feb 2018 Zhenxing Xu <xzxlnmail@163.com>
#

# Create result.csv
echo "TMax,GHSav,Iout,Vout,Power" > miner-result.csv

# Get raspberry IP address
IP=`cat slt-options.conf | sed -n '2p' | awk '{ print $1 }'`

# Create result directory
dirip="result-"$IP
mkdir $dirip

# CGMiner restart
for i in `seq 1 120`
do
    sleep 10
    echo "++++++++++++++++++++++++++++++ Running ++++++++++++++++++++++++++++++"

    # Debuglog switch
    dbg=`./ssh-login.exp $CIP cgminer-api debug | grep "\[Debug\] => true" | wc -l`
    if [ $dbg -eq 0 ]; then
        ./ssh-login.exp $CIP cgminer-api "debug\|D" > /dev/null
    fi

    # SSH no password
    ./ssh-login.exp $IP cgminer-api estats estats.log > /dev/null

    # Read CGMiner Log
    ./debuglog.sh $i
done

echo -e "\033[1;32m++++++++++++++++++++++++++++++  Done   ++++++++++++++++++++++++++++++\033[0m"
