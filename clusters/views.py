from django.shortcuts import render
from .models import Contig
import yaml

DOWNLOADS = {
    'IGV_VIEW_FN': 'data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.clusters.{type}.png',
    'FASTA_FN': 'data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.fasta',
    'BAM_CLUSTERS_FN': 'data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.clusters.bam',
    'BAI_CLUSTERS_FN': 'data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.clusters.bam.bai',
    'CONTIG_NAME': 'seq_{number}_{start_name}_{cl_type}_{cluster}_{sample}'
}

CLUSTERS_FN = 'static/data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.clusters.tsv'
SELECTED_CLUSTER_FN = 'static/data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.selected_cluster.yaml'
PAF_FN = 'static/data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.paf'

PAF_FORMAT = [('qname', 'string', 'Query sequence name'),
    ('qlen', 'int', 'Query sequence length'),
    ('qstart', 'int', 'Query start (0-based; BED-like; closed)'),
    ('qend', 'int', ' Query end (0-based; BED-like; open)'),
    ('strand', 'char', 'Relative strand: "+" or "-"'),
    ('tname', 'string', 'Target sequence name'),
    ('tlen', 'int', 'Target sequence length'),
    ('tstart', 'int', 'Target start on original strand (0-based)'),
    ('tend', 'int', 'Target end on original strand (0-based)'),
    ('nmatch', 'int', 'Number of residue matches'),
    ('alen', 'int', 'Alignment block length'),
    ('mapq', 'int', 'Mapping quality (0-255; 255 for missing)')]

def index(request):
    return render(request, 'clusters/index.html')

def igv(request):
    return render(request, 'clusters/igv.html')

def clusters(request):
    return render(request, 'clusters/clusters.html', { 'contigs': Contig.objects.all()})

def get_reads(clusters_fn):
    return [ { 'cluster_number': line.split()[0], 'name': line.split()[1]} for line in open( clusters_fn)]

def get_paf(paf_fn):
    return [ line.split('\t')[:12] for line in open(paf_fn)]

def get_selected_cluster(selected_cluster_fn):

    with open(selected_cluster_fn) as f:
        cluster_data = yaml.safe_load(f)
        selected_cluster = cluster_data['selected']
        return  f'{selected_cluster:03d}' 

def contig(request, p_id, p_number):
    contig = Contig.objects.get(pk = p_id)

    fn_kwargs = {
        'sample': contig.sample.name, 
        'start_name': contig.name, 
        'cl_type': 'nc', 
        'cluster': '000', 
        'type': 'collapsed', 
        'number': f'{p_number:03d}' 
    }

    clusters_fn = CLUSTERS_FN.format(**fn_kwargs)
    reads = get_reads(clusters_fn)

    selected_cluster_fn = SELECTED_CLUSTER_FN.format(**fn_kwargs)
    selected_cluster = get_selected_cluster(selected_cluster_fn)

    downloads = {}
    downloads['IGV_VIEW_FN'] = DOWNLOADS['IGV_VIEW_FN'].format(**fn_kwargs)
    downloads['FASTA_FN'] = DOWNLOADS['FASTA_FN'].format(**fn_kwargs)
    downloads['BAM_CLUSTERS_FN'] = DOWNLOADS['BAM_CLUSTERS_FN'].format(**fn_kwargs)
    downloads['BAI_CLUSTERS_FN']= DOWNLOADS['BAI_CLUSTERS_FN'].format(**fn_kwargs)
    downloads['CONTIG_NAME']= DOWNLOADS['CONTIG_NAME'].format(**fn_kwargs)
    
    paf_fn = PAF_FN.format(**fn_kwargs)

    return render(request, 'clusters/contig.html', {  'contig':  contig, 
                                                        'ranges': [range(contig.get_iterations_right + 1)] , 
                                                        'number': p_number, 
                                                        'reads': reads,
                                                        'downloads': downloads,
                                                        'selected_cluster': selected_cluster,
                                                        'paf_format': PAF_FORMAT ,
                                                        'pafs': ( {'name':  'hg38', 'alignments': get_paf(paf_fn)[:10]},
                                                                  {'name':  'panTro6','alignments': get_paf(paf_fn)[:10]})
                                                    })

