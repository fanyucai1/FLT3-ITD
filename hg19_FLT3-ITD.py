import os
import argparse
import subprocess

#Email:yucai.fan@illumina.com
#2021.09.01
#fix bug:2021.09.08 pindel insert length=max(read_length,mean_insert_length,median_insert_length)


docker_name="fanyucai1/flt3_itd:latest" #https://hub.docker.com/r/fanyucai1/flt3_itd

parser=argparse.ArgumentParser("This script will find FLT3_IDT.\n\n")
parser.add_argument("-b","--bam",help="bam file(required)",required=True)
parser.add_argument("-o","--outdir",help="output directory",default=os.getcwd())
parser.add_argument("-n","--name",help="sample name(required)",required=True)
parser.add_argument("-d","--dragen",help="dragen hg19 hash table")
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
subprocess.check_call('mkdir -p %s/FLT3-ITD'% (args.outdir), shell=True)

docker_run=" docker run -v %s:/Raw_data/ -v %s:/output/ %s "%(indir,args.outdir,docker_name)
#ScanITD
ScanITD=docker_run + "/software/python3/Python-v3.7.0/bin/python3 /software/ScanITD.py -i /Raw_data/%s -r /reference/hg19.fa  " \
         "-f 0.02 -l 3 -t /reference/FLT3.bed -o /output/ScanITD/%s "%(file_name,args.name)
subprocess.check_call(ScanITD,shell=True)
subprocess.check_call('cp %s/ScanITD/%s.itd.vcf %s/FLT3-ITD/%s.ScanITD.vcf'%(args.outdir,args.name,args.outdir,args.name),shell=True)

#FLT3_ITD_ext
FLT3_ITD_ext=docker_run + " perl /software/FLT3_ITD_ext.pl -b /Raw_data/%s -o /output/FLT3_ITD_ext/ "%(file_name)
subprocess.check_call(FLT3_ITD_ext,shell=True)
subprocess.check_call('cp %s/FLT3_ITD_ext/*.vcf %s/FLT3-ITD/%s_FLT3_ITD_ext.vcf'%(args.outdir,args.outdir,args.name),shell=True)

#pindel
insert_size=docker_run +'java -jar /software/picard.jar CollectInsertSizeMetrics I=/Raw_data/%s ' \
                        'O=/output/insert_size_metrics.txt H=/output/insert_size_histogram.pdf M=0.5'%(file_name)
subprocess.check_call(insert_size,shell=True)
infile=open("%s/insert_size_metrics.txt"%(args.outdir),"r")
num,k,size=0,0,0
for line in infile:
    num+=1
    array=line.strip().split("\t")
    if line.startswith("MEDIAN_INSERT_SIZE"):
        k=num
    if k!=0 and num==(k+1):
        size=max(int(float(array[0])),int(float(array[1])),int(float(array[5])))
        print(int(float(array[0])),int(float(array[1])),int(float(array[5])))
infile.close()

samtools=docker_run+'samtools stats /Raw_data/%s|grep ^RL'%(file_name)
a=subprocess.check_output(samtools,shell=True,stderr=subprocess.STDOUT)
print("Read length %s"%(a.split()[1]))
if size <int(a.split()[1]):
    size=int(a.split()[1])
print("Insert size length %s"%(size))
subprocess.check_call("echo /Raw_data/%s\t%s\t%s >%s/pindel/pindel.config"%(file_name,size,args.name,args.outdir),shell=True)
pindel=docker_run + '/software/pindel-master/pindel -f /reference/hg19.fa -i /output/pindel/pindel.config -c chr13 ' \
                        '-o /output/pindel/%s -j /reference/FLT3.bed '%(args.name)
subprocess.check_call(pindel,shell=True)

pindel2vcf=docker_run +'/software/pindel-master/pindel2vcf -r /reference/chr13.fa -R hg19 -P /output/pindel/%s -e 5 -he 0.01 -d 2021 ' \
                   '-v /output/pindel/%s.vcf'%(args.name,args.name)
subprocess.check_call(pindel2vcf,shell=True)

pindel_out=docker_run+'/software/python3/Python-v3.7.0/bin/python3 /software/pinITD.py -I /output/pindel/%s.vcf -O /output/pindel/%s'\
           %(args.name,args.name)
subprocess.check_call(pindel_out,shell=True)
subprocess.check_call('cp %s/pindel/*.pro.vcf %s/FLT3-ITD/%s.pindel.vcf'%(args.outdir,args.outdir,args.name),shell=True)
subprocess.check_call('cd %s && rm -rf pindel FLT3_ITD_ext ScanITD insert_size_histogram.pdf insert_size_metrics.txt'%(args.outdir),shell=True)

#dragen
if args.dragen:
    subprocess.check_call("echo 'chr13\t28607523\t28608437\tFLT3_exon14_exon15' >%s/FLT3.bed"%(args.outdir),shell=True)
    subprocess.check_call('mkdir -p %s/tmp/' % (args.outdir), shell=True)
    cmd="dragen -f -r %s --tumor-bam-input %s --enable-map-align false " \
        "--enable-variant-caller true --vc-target-bed %s/FLT3.bed " \
        "--enable-sv true --sv-call-regions-bed %s/FLT3.bed --sv-exome true " \
        "--output-directory %s/tmp/ --output-file-prefix %s " \
        "--sv-somatic-ins-tandup-hotspot-regions-bed /opt/edico/config/sv_somatic_ins_tandup_hotspot_hg19.bed" \
        %(args.dragen,args.bam,args.outdir,args.outdir,args.outdir,args.name)
    subprocess.check_call(cmd,shell=True)
    subprocess.check_call('gunzip %s/tmp/%s.hard-filtered.vcf.gz'%(args.outdir,args.name),shell=True)
    subprocess.check_call('gunzip %s/tmp/%s.sv.vcf.gz' % (args.outdir, args.name), shell=True)
    infile=open("%s/tmp/%s.hard-filtered.vcf"%(args.outdir,args.name),"r")
    outfile = open("%s/FLT3-ITD/%s.dragen.FLT3.txt" % (args.outdir, args.name), "w")
    for line in infile:
        if not line.startswith("#"):
            array=line.strip().split("\t")
            if array[6]=="PASS":
                if len(array[3])>=15 or len(array[4])>=15:
                    outfile.write("%s\n"%(line))
    infile.close()
    infile = open("%s/tmp/%s.sv.vcf" % (args.outdir, args.name), "r")
    for line in infile:
        if not line.startswith("#"):
            array=line.strip().split("\t")
            if array[6]=="PASS":
                outfile.write("%s\n"%(line))
    infile.close()
    outfile.close()
    subprocess.check_call('rm -rf %s/tmp/ %s/FLT3.bed'%(args.outdir,args.outdir),shell=True)