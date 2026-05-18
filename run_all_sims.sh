#!/bin/bash
export PATH=$PATH:/home/dev/6_sem/KURSACH_seti/02_model/omnetpp-6.0.3/bin
export LD_LIBRARY_PATH=/home/dev/6_sem/KURSACH_seti/02_model/inet4.5/src:$LD_LIBRARY_PATH

cd /home/dev/6_sem/KURSACH_seti/02_model/kursach_model

configs=("A_Base" "B_ReserveEnabled" "C_FailurePrimary" "D_ScaleUp")

for config in "${configs[@]}"
do
    echo "Running config: $config..."
    opp_run -u Cmdenv -c $config -n .:../inet4.5/src:../inet4.5/tutorials:../inet4.5/showcases --image-path=../inet4.5/images -l ../inet4.5/src/INET omnetpp.ini > "../../03_results/log_${config}.txt" 2>&1
    echo "Done $config."
    sleep 2
done
