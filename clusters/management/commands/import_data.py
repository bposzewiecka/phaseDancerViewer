import os

import yaml
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from clusters.models import Contig, Sample
from phaseDancerViewer.settings import DATA_DIRS


class Command(BaseCommand):
    help = "Importing sample data from configutation file."

    def add_arguments(self, parser):
        parser.add_argument("sample_names", nargs="+", type=str)

    def read_sample_config(self, config_fn):
        def save_config(obj, config):
            obj.iterations = config.get("iterations")
            obj.igv_screenshot = config.get("igv-screenshot")
            obj.browser = config.get("browser")
            obj.save()

        with open(config_fn) as f:

            config = yaml.safe_load(f)

            for sample_name, sample_config in config["samples"].items():

                try:
                    sample = Sample.objects.get(name=sample_name)
                    contigs = Contig.objects.filter(sample=sample)
                    contigs.delete()
                    sample.delete()

                except Sample.DoesNotExist:
                    pass

                sample = Sample.objects.create(name=sample_name)
                save_config(sample, sample_config)

                for contig_name in sample_config["contigs"]:

                    if type(sample_config["contigs"]) == list:
                        contig = Contig.objects.create(name=contig_name, sample=sample)
                    else:
                        contig = Contig.objects.create(name=contig_name, sample=sample)
                        contig_config = sample_config["contigs"][contig_name]
                        save_config(contig, contig_config)

                if contig.get_iterations() is None:
                    raise CommandError(
                        f'Iterations number is not set for sample "{sample_name}" and contig "{contig_name}".'
                    )

    @transaction.atomic
    def handle(self, *args, **options):

        config_files = []

        for sample_name in options["sample_names"]:

            sample_path = os.path.join(DATA_DIRS, sample_name)

            if not os.path.isdir(sample_path):
                raise CommandError(
                    f'Data from sample "{sample_name}" does not exist. Check if directory "{sample_path}" exists.'
                )

            config_fn = os.path.join(sample_path, "config.yaml")

            if not os.path.isfile(config_fn):
                raise CommandError(
                    f'Configuration file for sample "{sample_name}" does not exist. Check if file "{config_fn}" exists.'
                )

            config_files.append(config_fn)

        for config_fn in config_files:
            self.read_sample_config(config_fn)
