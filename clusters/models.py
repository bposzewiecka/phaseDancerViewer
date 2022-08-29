from django.db import models

SEQUENCING_TECHNOLOGIES = [
    ("pb", "PacBio"),
    ("hifi", "Oxford Nanopore"),
    ("ont", "PacBio HiFi"),
]


class Reference(models.Model):
    name = models.CharField(max_length=20)
    in_ucsc = models.BooleanField(default=False)

    def __str__(self):
        return self.name + (" (in UCSC)" if self.in_ucsc else "")

    class Meta:
        ordering = ["name"]


class PhaseDancerData(models.Model):
    iterations = models.IntegerField(null=True, blank=True)
    igv_screenshot = models.BooleanField(null=True)
    browser = models.BooleanField(null=True)
    mappings = models.ManyToManyField(Reference, blank=True)

    class Meta:
        abstract = True


class Sample(PhaseDancerData):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    technology = models.CharField(max_length=4, choices=SEQUENCING_TECHNOLOGIES)


class Contig(PhaseDancerData):
    name = models.CharField(max_length=50)
    sample = models.ForeignKey(Sample, on_delete=models.PROTECT, related_name="samples")

    ASSEMBLY_TYPES = (
        ("U", "From unique sequence"),
        ("C", "From cluster of sequences"),
    )

    assembly_type = models.CharField(max_length=1, choices=ASSEMBLY_TYPES)

    def get_property(self, assembly_prop, sample_prop, default_value):
        if assembly_prop is not None:
            return assembly_prop

        if sample_prop is not None:
            return sample_prop

        return default_value

    def get_iterations(self):
        return self.get_property(self.iterations, self.sample.iterations, 0)

    def get_igv_screenshot(self):
        return self.get_property(self.igv_screenshot, self.sample.igv_screenshot, False)

    def get_browser(self):
        return self.get_property(self.browser, self.sample.browser, False)

    def get_contig_size(self):
        return self.get_property(self.contig_size, self.sample.contig_size, None)

    def get_contig_extension_size(self):
        return self.get_property(
            self.contig_extension_size, self.sample.contig_extension_size, None
        )

    def get_reference_prefix_to_map_size(self):
        return self.get_property(
            self.reference_prefix_to_map_size,
            self.sample.reference_prefix_to_map_size,
            None,
        )

    def __str__(self):
        return self.name + " (" + self.sample.name + ")"
