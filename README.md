# FLT3-IDT数据分析

### 关于生信方面的最新综述文章

[Yuan D ,  He X ,  Han X , et al. Comprehensive review and evaluation of computational methods for identifying FLT3-internal tandem duplication in acute myeloid leukaemia[J]. Briefings in Bioinformatics, 2021.](https://academic.oup.com/bib/advance-article-abstract/doi/10.1093/bib/bbab099/6225087?redirectedFrom=fulltext)

### 关于FLT3-IDT变异

[Spencer D H ,  Abel H J ,  Lockwood C M , et al. Detection of FLT3 Internal Tandem Duplication in Targeted, Short-Read-Length, Next-Generation Sequencing Data[J]. The Journal of molecular diagnostics: JMD, 2012, 15(1).](https://www.sciencedirect.com/science/article/pii/S1525157812002590)

### 变异的大小范围：15～300bp,所该部分变异应该属于small variant +SV

### 流程说明

1. 本脚本使用FLT3_ITD_ext、pindel、ScanITD、dragen(非必须)四种方法检测FLT3-IDT,需输入bam文件（**基于hg19**）

2. 需先下载对应Docker安装包 [fanyucai1/flt3_itd](https://hub.docker.com/repository/docker/fanyucai1/flt3_itd)

3. python3 hg19_FLT3-ITD.py --help


        usage: This script will find FLT3_IDT.
        
         [-h] -b BAM [-o OUTDIR] -n NAME [-d DRAGEN]
        
        optional arguments:
          -h, --help            show this help message and exit
          -b BAM, --bam BAM     bam file(required)
          -o OUTDIR, --outdir OUTDIR
                                output directory
          -n NAME, --name NAME  sample name(required)
          -d DRAGEN, --dragen DRAGEN
                                dragen hg19 hash table