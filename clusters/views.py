import yaml
from django.shortcuts import render

from .models import Contig

COMPRESSION_TYPES = ("uncompressed", "compressed")
FILE_TYPES = ("BAM_CLUSTERS_FN", "BAI_CLUSTERS_FN", "FASTA_FN", "FAI_FN")

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
        "FAI_FN": "data/{sample}/{contig}/{assembler}/{cl_type}_{cluster}/seq_{number}/seq_{number}.{contig}.{cl_type}_{cluster}.{sample}.{assembler}."
        + compression
        + ".fasta.fai",
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

    iterations = contig.get_iterations()

    fn_kwargs = {
        "sample": contig.sample.name,
        "contig": contig.name,
        "cl_type": "nc",
        "cluster": "000",
        "type": "collapsed",
        "number": f"{p_number:03d}",
        "assembler": "minimap2",
    }

    FLANKING = 15

    before = p_number - FLANKING
    after = p_number + FLANKING + 1

    if before < 0:
        after = p_number + FLANKING - before

    if after > iterations:
        before = p_number - FLANKING - after + iterations

    current_ranges = list(range(max(0, before), min(after, iterations)))

    if iterations > 2 * FLANKING + 1:

        ranges_group_by = max(iterations // 20 // 5 * 5, 10)

        ranges = [
            list(
                range(
                    i * ranges_group_by,
                    min(i * ranges_group_by + ranges_group_by, iterations),
                )
            )
            for i in range((iterations + ranges_group_by - 1) // ranges_group_by)
        ]

        if len(ranges[-1]) == 1:
            ranges[-2] += ranges[-1]
            del ranges[-1]

    else:
        ranges = None

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

    contig_name = (
        "seq_{number}_{contig}_{cl_type}_{cluster}_{sample}_{assembler}".format(
            **fn_kwargs
        )
    )

    return render(
        request,
        "clusters/contig.html",
        {
            "contig": contig,
            "contig_name": contig_name,
            "ranges": ranges,
            "current_ranges": current_ranges,
            "number": p_number,
            "reads": reads,
            "files": files,
            "selected_cluster": selected_cluster,
            "paf_format": PAF_FORMAT,
            # 'pafs': ( {'name':  'hg38', 'alignments': get_paf(paf_fn)[:10]},
            #          {'name':  'panTro6','alignments': get_paf(paf_fn)[:10]})
        },
    )
