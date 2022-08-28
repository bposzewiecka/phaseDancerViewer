from django.contrib import admin

from clusters.models import Contig, Reference, Sample


class SampleAdmin(admin.ModelAdmin):
    pass


class ContigAdmin(admin.ModelAdmin):
    pass


class ReferenceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Sample, SampleAdmin)
admin.site.register(Contig, ContigAdmin)
admin.site.register(Reference, ReferenceAdmin)
