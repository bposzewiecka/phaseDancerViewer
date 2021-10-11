from django.db import models

SEQUENCING_TECHNOLOGIES = [
    ('pb', 'PacBio'),
    ('hifi', 'Oxford Nanopore'),
    ('ont', 'PacBio HiFi'),
]

class Reference(models.Model):
    name = models.CharField(max_length = 20, primary_key = True)
    in_ucsc = models.BooleanField(default = False) 

    def __str__(self):
        return self.name + (' (in UCSC)' if self.in_ucsc else '')

    class Meta:
        ordering = ['name']

class PhaseDancerData(models.Model):
    iterations_right = models.IntegerField(null = True, blank = True)
    iterations_left = models.IntegerField(null = True, blank = True)
    igv_screenshot = models.BooleanField(null = True)
    browser = models.BooleanField(null = True)
    contig_size = models.IntegerField(null = True, blank = True)
    contig_extension_size = models.IntegerField(null = True, blank = True)
    reference_prefix_to_map_size = models.IntegerField(null = True, blank = True)
    mappings = models.ManyToManyField(Reference, blank = True)

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

class Contig(PhaseDancerData):
    name = models.CharField(max_length = 50)
    sample =  models.ForeignKey(Sample, on_delete = models.PROTECT, related_name = 'samples') 

    ASSEMBLY_TYPES = (
        ('U', 'From unique sequence'),
        ('C', 'From cluster of sequences'),
    )

    assembly_type = models.CharField(max_length = 1, choices = ASSEMBLY_TYPES)

    def get_property(self, assembly_prop, sample_prop, default_value):
        if assembly_prop:
            return assembly_prop
        
        if sample_prop:
            return  sample_prop

        return default_value

    @property
    def get_iterations_right(self):
        return self.get_property(self.iterations_right, self.sample.iterations_right, 0)

    @property
    def get_iterations_left(self):
        return self.get_property(self.iterations_left, self.sample.iterations_left, 0)

    @property
    def get_igv_screenshot(self):
        return self.get_property(self.igv_screenshot, self.sample.igv_screenshot, False)

    @property
    def get_browser(self):
        return self.get_property(self.browser, self.sample.browser, False)

    @property
    def get_contig_size(self):
        return self.get_property(self.contig_size, self.sample.contig_size, None)

    @property
    def get_contig_extension_size(self):
        return self.get_property(self.contig_extension_size, self.sample.contig_extension_size, None)

    @property
    def get_reference_prefix_to_map_size(self):
        return self.get_property(self.reference_prefix_to_map_size, self.sample.reference_prefix_to_map_size, None)
  
    def __str__(self):
        return self.name + ' (' + self.sample.name + ')'
