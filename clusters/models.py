from django.db import models

class Sample(models.Model):
    name = models.CharField(max_length = 100, unique = True)    

    def __str__(self):
        return self.name

class Assembly(models.Model):
    name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 1000)
    start_name = models.CharField(max_length = 50)
    sample =  models.ForeignKey(Sample, on_delete = models.PROTECT, related_name='samples') 

    iterations_right = models.IntegerField()
    iterations_left = models.IntegerField()

    ASSEMBLY_TYPES = (
        ('U', 'From unique sequence'),
        ('C', 'From cluster of sequences'),
    )

    assembly_type = models.CharField(max_length = 1, choices = ASSEMBLY_TYPES)

    def __str__(self):
        return self.name + ' (' + self.sample.name + ')'