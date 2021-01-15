import boto3
import prefect
import re
import requests
import zipfile

from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
from prefect import task, Flow
from urllib.parse import urljoin

from data_pipelines.definition.versions import DictionaryVersion

CEDICT_URL = "https://www.mdbg.net/chinese/dictionary?page=cedict"
CEDICT_BASE_URL = "https://www.mdbg.net"
VERSION_REGEX = "Latest release: <strong>(.*)</strong>"
ENTRIES_REGEX = "Number of entries: <strong>(.*)</strong>"
URL_REGEX = ".*/cedict_1_0_ts_utf-8_mdbg.zip"


@task
def get_version():
    logger = prefect.context.get("logger")

    logger.info("Checking CEDICT page")
    response = requests.get(CEDICT_URL)
    page = BeautifulSoup(response.text, "html.parser")
    logger.info("Checked CEDICT page")

    version = get_match_or_none(response.text, VERSION_REGEX)
    entries = get_match_or_none(response.text, ENTRIES_REGEX)

    links = page.findAll("a", href=re.compile(URL_REGEX))
    link = ""
    if len(links) > 0:
        relative_link = links[0].get("href")
        link = urljoin(CEDICT_BASE_URL, relative_link)

    logger.info(
        "Found cedict version %s with %s entries at %s" % (version, entries, link)
    )

    return DictionaryVersion(version, link, entries)


@task
def move_dataset_to_s3(version):
    filename = "cedict_1_0_ts_utf-8_mdbg.zip"

    response = requests.get(version.link)
    with open(filename, "wb") as output:
        output.write(response.content)

    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(".")

    s3_client = boto3.client("s3")

    try:
        response = s3_client.upload_file(
            filename,
            "foreign-language-reader-content",
            "definitions/cedict/cedict_ts.u8",
        )
    except ClientError as e:
        print(e)


def get_match_or_none(text, pattern, group=1):
    matches = re.search(pattern, text)
    if matches:
        return matches.group(group)
    else:
        return ""


with Flow("CEDICT") as flow:
    version = get_version()
    live_data = move_dataset_to_s3(version)
