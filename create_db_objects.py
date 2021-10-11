def addReferences():

    from clusters.models import Reference

    references = ['hg38', 'hg19', 'panTro6', 'panTro5', 'panPan3', 'gorGor6', 'ponAbe3', 'nomLue3']

    for reference in references:
        Reference.objects.create(name = reference, in_ucsc = True)

addReferences()