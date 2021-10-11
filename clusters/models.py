from django.db import models

SEQUENCING_TECHNOLOGIES = [
    ('pb', 'PacBio'),
    ('hifi', 'Oxford Nanopore'),
    ('ont', 'PacBio HiFi'),
]

class Mapping(models.Model):
    name = models.CharField(max_length = 20)
    in_ucsc = models.BooleanField(default = False) 

class PhaseDancerData(models.Model):
    iterations_right = models.IntegerField(default = 0, null = True, blank = True)
    iterations_left = models.IntegerField(default = 0, null = True, blank = True)
    igv_screenshot = models.BooleanField(default = False)
    browser = models.BooleanField(default = True)
    contig_size = models.IntegerField(null = True, blank = True)
    contig_extension_size = models.IntegerField(null = True, blank = True)
    reference_prefix_to_map_size = models.IntegerField(null = True, blank = True)
    mappings = models.ManyToManyField(Mapping, blank = True)

    class Meta:
        abstract = True
    
class Sample(PhaseDancerData):
    name = models.CharField(max_length = 100, unique = True)    

    def __str__(self):
        return self.name

    technology = models.CharField(
        max_length = 4,
        choices = SEQUENCING_TECHNOLOGIES
    )

class Assembly(PhaseDancerData):
    start_name = models.CharField(max_length = 50)
    sample =  models.ForeignKey(Sample, on_delete = models.PROTECT, related_name = 'samples') 

    ASSEMBLY_TYPES = (
        ('U', 'From unique sequence'),
        ('C', 'From cluster of sequences'),
    )

    assembly_type = models.CharField(max_length = 1, choices = ASSEMBLY_TYPES)


    def __str__(self):
        return self.name + ' (' + self.sample.name + ')'
