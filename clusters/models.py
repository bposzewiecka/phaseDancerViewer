from django.db import models


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


class Contig(PhaseDancerData):
    name = models.CharField(max_length=50)
    sample = models.ForeignKey(Sample, on_delete=models.PROTECT, related_name="samples")

    def get_property(self, assembly_prop, sample_prop, default_value):
        if assembly_prop is not None:
            return assembly_prop

        if sample_prop is not None:
            return sample_prop

        return default_value

    def get_iterations(self):
        return self.get_property(self.iterations, self.sample.iterations, None)

    def get_igv_screenshot(self):
        return self.get_property(self.igv_screenshot, self.sample.igv_screenshot, False)

    def get_browser(self):
        return self.get_property(self.browser, self.sample.browser, True)

    def __str__(self):
        return self.name + " (" + self.sample.name + ")"
