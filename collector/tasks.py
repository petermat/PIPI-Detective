import logging
import os
from django.utils import timezone
from datetime import datetime

from collector.models import Pipipackage

# celery logging
#from celery.utils.log import get_task_logger
#logging.basicConfig(level=logging.INFO)

# pip install feedparser
def get_new_packages():
    import feedparser

    Feed = feedparser.parse('https://pypi.org/rss/packages.xml')
    for entry in Feed.entries:

        pipi_obj, new = Pipipackage.objects.update_or_create(name=entry.title.replace(" added to PyPI",""))
        if new:
            pipi_obj.summary = entry.summary
            pipi_obj.created = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
            pipi_obj.save()

            print(f"New package added to New: {pipi_obj.name}")
            print('Link:', entry.link)
            print('Published Date:', entry.published)
            print('Summary:', entry.summary)
            print()

# pip install google-cloud-bigquery
def get_most_downloaded_packages(n=10000):
    """
    run every 30 days and store these in database for fuzzy matching and definning known good behaviour
    """

    #"""
    from google.cloud import bigquery
    from google.oauth2 import service_account

    credentials = service_account.Credentials.from_service_account_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'oauth.json'))
    client = bigquery.Client(credentials=credentials, project=credentials.project_id, )
    #client = bigquery.Client()
    #         SELECT file.project, COUNT(*) as download_count, file.version, timestamp
    query = f"""
        SELECT file.project ,COUNT(*) as download_count
        FROM `bigquery-public-data.pypi.file_downloads`
        WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY file.project
        ORDER BY download_count DESC
        LIMIT {n}
    """
    #query_job = client.query(query)
    #results = query_job.result()

    query_df = client.query_and_wait(query).to_dataframe()
    query_df.to_csv("bigquery.csv")

    #"""


def load_top_from_csv(path=None):
    import csv
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bigquery.csv')

    with open(path, "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            if i: # skipping header
                pipi_obj, new = Pipipackage.objects.update_or_create(name=line[0])
                pipi_obj.top_rating = line[1]
                pipi_obj.save()

                if new:
                    print(f"New package added to TOP10K: {line[0]} ({line[1]})")
