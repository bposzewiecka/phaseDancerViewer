from django.contrib import admin
from clusters.models import Sample, Assembly

class SampleAdmin(admin.ModelAdmin):
    pass

class AssemblyAdmin(admin.ModelAdmin):
    pass

admin.site.register(Sample, SampleAdmin)
admin.site.register(Assembly, AssemblyAdmin)