import os
import sys
import argparse
import subprocess

#Email:yucai.fan@illumina.com
#Update:2021.08.

docker_name="fanyucai1/flt3_itd:latest" #https://hub.docker.com/r/fanyucai1/flt3_itd

parser=argparse.ArgumentParser("This script will find FLT3_IDT.\n\n")
parser.add_argument("-b","--bam",help="bam file",required=True)
parser.add_argument("-o","--outdir",help="output directory")
parser.add_argument("-n","--name",help="sample name")
parser.add_argument("-i","--insert",help="insert length",required=True)
args=parser.parse_args()

#set directory
bam=os.path.abspath(args.bam)
indir=os.path.dirname(bam)
file_name=os.path.basename(bam)
subprocess.check_call('mkdir -p %s'%(args.outdir),shell=True)
args.outdir=os.path.abspath(args.outdir)
subprocess.check_call('mkdir -p %s/pindel' % (args.outdir), shell=True)
subprocess.check_call('mkdir -p %s/FLT3_ITD_ext' % (args.outdir), shell=True)
subprocess.check_call('mkdir -p %s/ScanITD' % (args.outdir), shell=True)

docker_run=" docker run -ti -v %s:/Raw_data/ -v %s:/output/ %s "%(indir,args.outdir,docker_name)

#ScanITD
ScanITD=docker_run + "/software/python3/Python-v3.7.0/bin/python3 /software/ScanITD.py -i /Raw_data/%s -r /reference/hg19.fa  " \
         "-f 0.02 -l 3 -t /reference/FLT3.bed -o /output/ScanITD/%s "%(file_name,args.name)
subprocess.check_call(ScanITD,shell=True)

#FLT3_ITD_ext
FLT3_ITD_ext=docker_run + " perl /software/FLT3_ITD_ext.pl -b /Raw_data/%s -o /output/FLT3_ITD_ext/ "%(file_name)
subprocess.check_call(FLT3_ITD_ext,shell=True)

#pindel
subprocess.check_call("echo /Raw_data/%s\t%s\t%s >%s/pindel/pindel.config"%(file_name,args.insert,args.name,args.outdir),shell=True)
pindel=docker_run + '/software/pindel-master/pindel -f /reference/hg19.fa -i /output/pindel/pindel.config -c chr13 ' \
                        '-o /output/pindel/%s -j /reference/FLT3.bed '%(args.name)
subprocess.check_call(pindel,shell=True)

pindel2vcf=docker_run +'/software/pindel-master/pindel2vcf -r /reference/chr13.fa -R hg19 -P /output/pindel/%s -e 5 -he 0.01 -d 2021 ' \
                   '-v /output/pindel/%s.vcf'%(args.name,args.name)
subprocess.check_call(pindel2vcf,shell=True)

pindel_out=docker_run+'/software/python3/Python-v3.7.0/bin/python3 /software/pinITD.py -I /output/pindel/%s.vcf -O /output/pindel/%s'\
           %(args.name,args.name)
subprocess.check_call(pindel_out,shell=True)

#dragen=SNV+SV
