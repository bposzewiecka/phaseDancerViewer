from django.shortcuts import render
from .models import Assembly
import yaml

#f'data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.clusters.{type}.png'

DOWNLOADS_FN = {
    'IGV_VIEW_FN': 'data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.clusters.{type}.png',
    'FASTA_FN': 'data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.fasta',
    'BAM_CLUSTERS_FN': 'data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.clusters.bam',
    'BAI_CLUSTERS_FN': 'data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.clusters.bai'
}

CLUSTERS_FN = 'static/data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.clusters.tsv'
SELECTED_CLUSTER_FN = 'static/data/{sample}/{start_name}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.selected_cluster.yaml'

def index(request):
    return render(request, 'clusters/index.html')

def igv(request):
    return render(request, 'clusters/igv.html')

def clusters(request):
    return render(request, 'clusters/clusters.html', { 'assemblies': Assembly.objects.all()})

def get_reads(clusters_fn):
    return [ { 'cluster_number': line.split()[0], 'name': line.split()[1]} for line in open( clusters_fn)]

def get_selected_cluster(selected_cluster_fn):

    with open(selected_cluster_fn) as f:
        cluster_data = yaml.safe_load(f)
        selected_cluster = cluster_data['selected']
        return  f'{selected_cluster:03d}' 

def assembly(request, p_id, p_number):
    assembly = Assembly.objects.get(pk = p_id)

    fn_kwargs = {
        'sample': assembly.sample.name, 
        'start_name': assembly.start_name, 
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
    downloads['IGV_VIEW_FN'] = DOWNLOADS_FN['IGV_VIEW_FN'].format(**fn_kwargs)
    downloads['FASTA_FN'] = DOWNLOADS_FN['FASTA_FN'].format(**fn_kwargs)
    downloads['BAM_CLUSTERS_FN'] = DOWNLOADS_FN['BAM_CLUSTERS_FN'].format(**fn_kwargs)
    downloads['BAI_CLUSTERS_FN']= DOWNLOADS_FN['BAI_CLUSTERS_FN'].format(**fn_kwargs)
    
    return render(request, 'clusters/assembly.html', {  'assembly': assembly, 
                                                        'range': range(assembly.iterations_right + 1) , 
                                                        'number': p_number, 
                                                        'reads': reads,
                                                        'downloads': downloads,
                                                        'selected_cluster': selected_cluster
                                                        })