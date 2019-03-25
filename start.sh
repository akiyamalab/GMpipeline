#!/bin/sh

file=main.sh
python_path=`which python`
touch $file
echo '#!/bin/sh' > $file
echo '#$ -cwd' >> $file
echo '#$ -l f_node=1' >> $file
echo '#$ -l h_rt=01:00:00' >> $file
echo 'pwd' >> $file

## divide fasta -> create all jobs
echo "$python_path inputParser.py inputFile" >> $file

## submit jobs to nodes
echo 'for i in $(seq 1 $(cat N.txt)); do' >> $file
echo 'echo chmod u+x align_$i.sh' >> $file
echo 'chmod u+x align_$i.sh' >> $file
echo "/apps/t3/sles12sp2/uge/latest/bin/lx-amd64/qsub -g $1 align_\$i.sh" >> $file
echo 'done' >> $file

## compute comparison -> extract biome
echo 'chmod u+x comparison.sh' >> $file
echo "/apps/t3/sles12sp2/uge/latest/bin/lx-amd64/qsub -g $1 comparison.sh" >> $file

chmod u+x $file
qsub -g $1 $file
