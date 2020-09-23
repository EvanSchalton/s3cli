# s3cli

Toy example of a cli to list details for an account's s3 buckets

# Install

Install directly from github with the following command:
python -m pip install git+https://github.com/EvanSchalton/s3cli.git

# Setup

s3cli requires a json config file made available via an environment variable.
The config should contain the follows:
```
{
  "region_name": "",
  "aws_access_key_id": "",
  "aws_secret_access_key": ""
}
```
you can reference/copy the aws_config_template.json file
The AWS details can be found in the IAM service on AWS.

There's a command in the CLI to set this environment variable, but you can optionally set it directly in the terminal
```s3cli set-config PATH-TO-YOUR-CONFIG-JSON```

# Usage

The main features are broken down into two sections, all buckets or single bucket:

## All Buckets Commands

Display an ASCII table in the terminal with: ```s3cli show-table --unit=Mb```
Save an excel or csv of the table details to the specified path: ```s3cli save-table SAVE_AS_PATH.csv|.xlsx --unit=Mb```
List all of the bucket names: ```s3cli list-buckets```

## Single Bucket Command

Display the details of the given bucket: ```s3cli bucket-details --bucket=BUCKETNAME --unit=mb```

# Results

The details (for tables or single bucket command) are as follows:
```
{
  "name": BucketName,
  "creation_date": DATETIME,
  "count": KEY-COUNT,
  "last_modified": DATETIME,
  "size (SPECIFIED-UNIT)": DISK-SIZE
}
```
