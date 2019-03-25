#!/usr/bin/env python
#coding: UTF-8

import configparser
import sys
from Bio import SeqIO

config = configparser.RawConfigParser()
filename = sys.argv[1]
path = 'PATH' 
divide = 'STAGE:DIVIDE_FASTA_FILE'
ghost = 'STAGE:RUN_GHOSTZ-GPU'
rma6 = 'STAGE:RUN_BLAST2RMA6'
comparison = 'STAGE:RUN_COMPUTE-COMPARISON' 
biome = 'STAGE:RUN_EXTRACT-BIOME'
joboption = '#!/bin/sh\n#$ -cwd\n#$ -l f_node=1\n#$ -l h_rt=3:00:00\n' # get from inputFile too?? #izittayo!!!!!!!!!
joboption2 = '#!/bin/sh\n#$ -cwd\n#$ -l f_node=1\n#$ -l h_rt=0:10:00\n'
config.optionxform = str
config.read(filename)

def main():
    if config.has_section(divide):
        for key in config[divide]:
            if config[divide][key] == "":
                ### NO OPTION
                pass
            else:
                pass
        divide_fasta(config[divide]['fasta'], int(config[divide]['n']))
        with open('N.txt', 'w') as f:
            f.write(config[divide]['n'])

    if config.has_section(ghost):
        command_0 = config[path]['ghostz-gpu'] + " aln"
        for key in config[ghost]:
            if config[ghost][key] == "":
                ### NO OPTION
                pass
            else:
                command_0 += " -" + key + " " + config[ghost][key]
        for i in range(int(config[divide]['n'])):
            jobfile = "align_" + str(i+1) + ".sh"
            with open(jobfile, 'w') as f:
                f.write(joboption + "#$ -N alignjob_" + str(i+1) + "\n" + command_0 + " -i " + str(i+1) + ".fasta -o ghostout_" + str(i+1) + "\n")

    if config.has_section(rma6):
        command_1 = config[path]['blast2rma']
        for key in config[rma6]:
            if config[rma6][key] == "":
                ### no option
                pass
            else:
                command_1 += " --" + key + " " + config[rma6][key]
        for i in range(int(config[divide]['n'])):
            jobfile = "align_" + str(i+1) + ".sh"
            with open(jobfile, 'a') as f:
                f.write(command_1 + " --in ghostout_" + str(i+1) + " --out " + str(i+1) + ".rma6 --format BlastTab\n")

    if config.has_section(comparison):
        command_2 = config[path]['compute-comparison']
        for key in config[comparison]:
            if config[comparison][key] == "":
                ### no option
                pass
            else:
                command_2 += " --" + key + " " + config[comparison][key]
        jobfile = "comparison.sh"
        with open(jobfile, 'w') as f:
            f.write(joboption2 + "#$ -hold_jid ")
            for i in range(int(config[divide]['n'])):
                if i != int(config[divide]['n'])-1:
                    f.write("alignjob_" + str(i+1) + ",")
                else:
                    f.write("alignjob_" + str(i+1))
            f.write("\nXvfb :99 &\nexport DISPLAY=:99\n" + command_2 + " --in")
            for i in range(int(config[divide]['n'])):
                f.write(" " + str(i+1) + ".rma6")
            f.write('\n')

    if config.has_section(biome):
        command_3 = config[path]['extract-biome']
        for key in config[biome]:
            if config[biome][key] == "":
                ### no option
                pass
            else:
                command_3 += " --" + key + " " + config[biome][key]
        with open(jobfile, 'a') as f:
            f.write(command_3 + " --in " + config[comparison]['out'] + "\n")

def divide_fasta(filename, n):
    seqnum = len(list(SeqIO.parse(open(filename), "fasta"))) #sequence length

    filenum = int((seqnum-seqnum%n)/n) # div_n reads in a .fasta
    outList = []

    if n > seqnum:
        print("can't divide into " + str(n) + " fasta file. (too small sequence number)")
        sys.exit()

    #create outfile
    for x in range(1, n+1):
        w = open(str(x) + ".fasta", "w")
        outList.append(w)

    #write file
    for i, record in enumerate(SeqIO.parse(open(filename), "fasta")):
        tmp = i + 1
        if tmp >= filenum * n:
            filenumber = int((tmp-tmp%filenum)/filenum)-1
        else:
            filenumber = int((tmp - tmp%filenum)/filenum)
        outfile = outList[filenumber]
        outfile.write(">" + str(record.description) + "\n")
        outfile.write(str(record.seq) + "\n")
        
    #close file
    for out in outList:
        out.close()


main()
