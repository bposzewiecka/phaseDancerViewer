import os

import yaml
from django.shortcuts import render

from .models import Contig, Sample

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

DIRECTORY_FN = (
    "static/data/{sample}/{contig}/{assembler}/{cl_type}_{cluster}/seq_{number}/"
)
CLUSTERS_FN = "static/data/{sample}/{contig}/{assembler}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{contig}.{cl_type}_{cluster}.{sample}.{assembler}.clusters.tsv"
SELECTED_CLUSTER_FN = "static/data/{sample}/{contig}/{assembler}/{cl_type}_{cluster}/seq_{number}/clusters/seq_{number}.{contig}.{cl_type}_{cluster}.{sample}.{assembler}.selected_cluster.yaml"
# PAF_FN = 'static/data/{sample}/{start_name}/{cl_type}_{cluster}/minimap2/seq_{number}/seq_{number}.{start_name}.{cl_type}_{cluster}.{sample}.paf'

COMPRESSION_TYPES_VIEW_MODES = [
    {"type": "C", "name": "Homopolymer compressed"},
    {"type": "U", "name": "Uncompressed"},
    {"type": "B", "name": "Both"},
]

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


CONFIG_FILE_NAME = "static/config.yaml"


def read_config():

    Contig.objects.all().delete()
    Sample.objects.all().delete()

    with open(CONFIG_FILE_NAME) as f:

        samples_data = yaml.safe_load(f)

        for sample_name, sample_data in samples_data["samples"].items():

            iterations = sample_data.get("iterations")
            sample_db = Sample.objects.create(name=sample_name, iterations=iterations)

            for contig_name in sample_data["contigs"]:

                iterations = None

                if isinstance(sample_data["contigs"], dict):
                    iterations = sample_data["contigs"][contig_name].get("iterations")

                Contig.objects.create(
                    name=contig_name, iterations=iterations, sample=sample_db
                )


def index(request):

    if not Contig.objects.count():
        read_config()

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


def get_ranges(iterations, number):

    FLANKING = 15

    before = number - FLANKING
    after = number + FLANKING + 1

    if before < 0:
        after = number + FLANKING - before

    if after > iterations:
        before = number - FLANKING - after + iterations

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

    return ranges, current_ranges


def contig(request, p_id, p_number, p_type):

    contig = Contig.objects.get(pk=p_id)

    ranges, current_ranges = get_ranges(contig.get_iterations(), p_number)

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
    directory_fn = DIRECTORY_FN.format(**fn_kwargs)

    contig_name = (
        "seq_{number}_{contig}_{cl_type}_{cluster}_{sample}_{assembler}".format(
            **fn_kwargs
        )
    )

    context = {
        "contig": contig,
        "contig_name": contig_name,
        "ranges": ranges,
        "current_ranges": current_ranges,
        "number": p_number,
        "paf_format": PAF_FORMAT,
        "type": p_type,
        "view_modes": COMPRESSION_TYPES_VIEW_MODES,
        # 'pafs': ( {'name':  'hg38', 'alignments': get_paf(paf_fn)[:10]},
        #          {'name':  'panTro6','alignments': get_paf(paf_fn)[:10]})
    }

    if not os.path.isdir(directory_fn):
        context["status"] = 1

        return render(request, "clusters/contig.html", context)

    reads = get_reads(clusters_fn)

    context["reads"] = reads

    selected_cluster_fn = SELECTED_CLUSTER_FN.format(**fn_kwargs)
    selected_cluster = get_selected_cluster(selected_cluster_fn)

    context["selected_cluster"] = selected_cluster

    files = {
        compression: {
            file_type: FILES[compression][file_type].format(**fn_kwargs)
            for file_type in FILE_TYPES
        }
        for compression in COMPRESSION_TYPES
    }

    context["files"] = files
    context["status"] = 0

    return render(request, "clusters/contig.html", context)
