import yaml

from clusters.models import Contig, Sample

CONFIG_FILE_NAME = "static/data/config.yaml"


def read_config():

    Contig.objects.all().delete()
    Sample.objects.all().delete()

    with open(CONFIG_FILE_NAME) as f:

        samples_data = yaml.safe_load(f)

        for sample_name, sample_data in samples_data["samples"].items():

            iterations = sample_data.get("iterations")
            sample_db = Sample.objects.create(name=sample_name, iterations=iterations)

            for contig_name in sample_data["contigs"]:

                iterations = None

                if isinstance(sample_data["contigs"], dict):
                    iterations = sample_data["contigs"][contig_name].get("iterations")

                Contig.objects.create(
                    name=contig_name, iterations=iterations, sample=sample_db
                )


read_config()
