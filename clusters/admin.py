from django.contrib import admin
from clusters.models import Sample, Assembly

class SampleAdmin(admin.ModelAdmin):
    pass

class AssemblyAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_name', 'sample', 'iterations_right', 'iterations_left')

admin.site.register(Sample, SampleAdmin)
admin.site.register(Assembly, AssemblyAdmin)