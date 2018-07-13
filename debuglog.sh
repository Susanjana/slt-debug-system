#!/bin/bash
#
# Author Feb 2018 Zhenxing Xu <xzxlnmail@163.com>
#

IP=`cat slt-options.conf | sed -n '2p' | awk '{ print $1 }'`
dirname=$IP"-"$1
mkdir $dirname

cat estats.log  | grep "\[MM ID" > ./$dirname/CGMiner_Debug.log

rm estats.log
cd ./$dirname

for i in CGMiner_Debug.log
do
    cat $i | sed 's/] /\]\n/g' | grep TMax  | sed 's/TMax\[//g'  | sed 's/\]//g' > $i.TMax
    cat $i | sed 's/] /\]\n/g' | grep WU    | sed 's/WU\[//g'    | sed 's/\]//g' > $i.WU
    cat $i | sed 's/] /\]\n/g' | grep "Iout\[" | sed 's/Iout\[//g' | sed 's/\]//g' > $i.Iout
    cat $i | sed 's/] /\]\n/g' | grep V0 | awk '{ print $3 }' > $i.Vout
    cat $i | sed 's/] /\]\n/g' | grep "Power" | sed 's/Power\[//g' | sed 's/\]//g' > $i.power

    # According to WU value, calculate GHSav.
    # Formula: ghsav = WU / 60 * 2^32 /10^9
    cat $i.WU | awk '{printf ("%.2f\n", ($1/60*2^32/10^9))}' > $i.GHSav

    paste -d, $i.TMax $i.GHSav $i.Iout $i.Vout $i.power >> ../miner-result.csv

    rm -rf $i.TMax $i.WU $i.GHSav $i.Iout $i.Vout $i.power

    cd ..
    mv ./$dirname ./result*
done
