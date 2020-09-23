import pytest
import pandas as pd
from timeit import timeit

from ..s3connection import connect
from ..s3review import s3Reviewer

TIMEIT_COUNT = 1

@pytest.fixture(scope="session")
def sdk_client(request):
    return connect()

@pytest.fixture(scope="session")
def cli_client(request):
    return s3Reviewer()

def test_list_buckets(cli_client, sdk_client):
    """Checks that the sdk and client provide the same results"""

    cli_bucket_list = [bucket.name for bucket in cli_client.buckets]
    sdk_bucket_list = [bucket.name for bucket in sdk_client.buckets.all()]

    for bucket in cli_bucket_list:
        assert bucket in sdk_bucket_list
        
    for bucket in sdk_bucket_list:
        assert bucket in cli_bucket_list

def test_bucket_lookup_by_name(cli_client):
    for bucket in cli_client.buckets:
        assert cli_client.getBucket(bucket.name) == bucket

def test_get_bucket_metrics(cli_client, sdk_client):

    for sdk_bucket in sdk_client.buckets.all():
        cli_bucket = cli_client.getBucket(sdk_bucket.name)
        cli_bucket_detail = cli_bucket.details()
        
        sizes = []
        modified = []
        bucket_items = [(sizes.append(item.size), modified.append(item.last_modified)) for item in sdk_bucket.objects.all()]
        
        sdk_count = len(bucket_items)
        sdk_size = sum(sizes)

        try:
            last_modified = max(modified)
        except:
            last_modified = sdk_bucket.creation_date

        assert sdk_bucket.creation_date == cli_bucket_detail['creation_date']
        assert sdk_count == cli_bucket_detail['count']
        assert sdk_size == cli_bucket_detail['size']
        assert last_modified == cli_bucket_detail['last_modified']

def test_preload_bucket_load():
    """Iniitalizing the client w/out intitalizing the buckets should be faster"""

    unloaded_time = timeit(
        setup = "from s3review import s3Reviewer",
        stmt = "unloaded_cli_client = s3Reviewer(preload=False)",
        number = TIMEIT_COUNT
    )

    preloaded_time = timeit(
        setup = "from s3review import s3Reviewer",
        stmt = "preloaded_cli_client = s3Reviewer(preload=True)",
        number = TIMEIT_COUNT
    )

    assert unloaded_time < preloaded_time

def test_preload_bucket_details():
    """Accessing pre-initialized buckets should be faster"""

    unloaded_cli_client = s3Reviewer(preload=False)
    preloaded_cli_client = s3Reviewer(preload=True)


    unloaded_time = timeit(
        setup = "from s3review import s3Reviewer\nunloaded_cli_client = s3Reviewer(preload=False)",
        stmt = "{bucket.name: bucket.details(calculate=True) for bucket in unloaded_cli_client.buckets}",
        number = TIMEIT_COUNT
    )

    preloaded_time = timeit(
        setup = "from s3review import s3Reviewer\npreloaded_cli_client = s3Reviewer(preload=True)",
        stmt = "{bucket.name: bucket.details() for bucket in preloaded_cli_client.buckets}",
        number = TIMEIT_COUNT
    )

    assert unloaded_time > preloaded_time

def test_client_can_create_a_dataframe(cli_client):
    assert(isinstance(cli_client.table(), pd.DataFrame))

def test_can_show_s3_table(cli_client):
    assert cli_client.showDetails(unit="kb")

def test_can_list_bucket_names(cli_client):
    assert all([isinstance(bucketName, str) for bucketName in cli_client.list])