import yaml
from django.shortcuts import render

from .models import Contig

COMPRESSION_TYPES = ("uncompressed", "compressed")
FILE_TYPES = ("BAM_CLUSTERS_FN", "BAI_CLUSTERS_FN", "FASTA_FN")

FILES = {
    compression: {
        "BAM_CLUSTERS_FN": "data/{sample}/{contig}/{assembler}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{contig}.{cl_type}_{cluster}.{sample}.{assembler}.clusters."
        + compression
        + ".bam",
        "BAI_CLUSTERS_FN": "data/{sample}/{contig}/{assembler}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{contig}.{cl_type}_{cluster}.{sample}.{assembler}.clusters."
        + compression
        + ".bam.bai",
        "FASTA_FN": "data/{sample}/{contig}/{assembler}/{cl_type}_{cluster}/seq_{number}/seq_{number}.{contig}.{cl_type}_{cluster}.{sample}.{assembler}."
        + compression
        + ".fasta",
    }
    for compression in COMPRESSION_TYPES
}

CLUSTERS_FN = "static/data/{sample}/{contig}/{assembler}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{contig}.{cl_type}_{cluster}.{sample}.{assembler}.clusters.tsv"
SELECTED_CLUSTER_FN = "static/data/{sample}/{contig}/{assembler}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{contig}.{cl_type}_{cluster}.{sample}.{assembler}.selected_cluster.yaml"
# PAF_FN = 'static/data/{sample}/{start_name}/{cl_type}_{cluster}/minimap2/seq_{number}/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.paf'

PAF_FORMAT = [
    ("qname", "string", "Query sequence name"),
    ("qlen", "int", "Query sequence length"),
    ("qstart", "int", "Query start (0-based; BED-like; closed)"),
    ("qend", "int", " Query end (0-based; BED-like; open)"),
    ("strand", "char", 'Relative strand: "+" or "-"'),
    ("tname", "string", "Target sequence name"),
    ("tlen", "int", "Target sequence length"),
    ("tstart", "int", "Target start on original strand (0-based)"),
    ("tend", "int", "Target end on original strand (0-based)"),
    ("nmatch", "int", "Number of residue matches"),
    ("alen", "int", "Alignment block length"),
    ("mapq", "int", "Mapping quality (0-255; 255 for missing)"),
]


def index(request):
    return render(request, "clusters/index.html", {"contigs": Contig.objects.all()})


def igv(request):
    return render(request, "clusters/igv.html")


def get_reads(clusters_fn):

    with open(clusters_fn) as f:
        return [
            {"cluster_number": line.split()[0], "name": line.split()[1]} for line in f
        ]


def get_paf(paf_fn):

    with open(paf_fn) as f:
        return [line.split("\t")[:12] for line in f]


def get_selected_cluster(selected_cluster_fn):

    with open(selected_cluster_fn) as f:
        cluster_data = yaml.safe_load(f)
        selected_cluster = cluster_data["selected"]
        return f"{selected_cluster:03d}"


def contig(request, p_id, p_number):

    contig = Contig.objects.get(pk=p_id)

    fn_kwargs = {
        "sample": contig.sample.name,
        "contig": contig.name,
        "cl_type": "nc",
        "cluster": "000",
        "type": "collapsed",
        "number": f"{p_number:03d}",
        "assembler": "minimap2",
    }

    clusters_fn = CLUSTERS_FN.format(**fn_kwargs)
    reads = get_reads(clusters_fn)

    selected_cluster_fn = SELECTED_CLUSTER_FN.format(**fn_kwargs)
    selected_cluster = get_selected_cluster(selected_cluster_fn)

    files = {
        compression: {
            file_type: FILES[compression][file_type].format(**fn_kwargs)
            for file_type in FILE_TYPES
        }
        for compression in COMPRESSION_TYPES
    }

    return render(
        request,
        "clusters/contig.html",
        {
            "contig": contig,
            "ranges": [range(contig.get_iterations() + 1)],
            "number": p_number,
            "reads": reads,
            "files": files,
            "selected_cluster": selected_cluster,
            "paf_format": PAF_FORMAT,
            # 'pafs': ( {'name':  'hg38', 'alignments': get_paf(paf_fn)[:10]},
            #          {'name':  'panTro6','alignments': get_paf(paf_fn)[:10]})
        },
    )
