
import click
import os
from .s3review import s3Reviewer
from difflib import get_close_matches
import subprocess
import platform

__author__ = "Evan Schalton"

@click.group()
def main():
    """Simple CLI for reviewing s3 buckets by Evan Schalton
    
    \b
    If this is your first time using the s3Rev CLI please run the
    `python s3Rev setup-guide` command for more information
    
    """
    pass

### CLI SETUP

@main.command()
def setup_guide():
    """Brief setup guide"""
    click.echo("""
    Create a json file (AWS_S3_CONFIG.json) with the following attributes:\n
    {
        "region_name": "YOUR-REGION",
        "aws_access_key_id": "YOUR-ID",
        "aws_secret_access_key": "YOUR-KEY"
    }

    \b
    Then add that file path to your environment variables with the following key:
    'S3CLI_AWS_USER_CONFIG'
    
    You can do that through your os or by using the 'set-config' command:
    `python s3Rev set-config YOUR-FILE-PATH`
    
    Now that you're all setup, run the --help command to learn about the s3Rev commands
    `python s3Rev --help`
    """)

@main.command()
@click.argument('path')
def set_config(path):
    """
    \b
    Saves the your AWS config json path to the environment variable 'S3CLI_AWS_USER_CONFIG'
    Ex: `python s3Rev set-config PATH_TO_CONFIG.json`
    """
    if os.path.exists(path):
        try:    

            os.environ['S3CLI_AWS_USER_CONFIG'] = path

            OSName = platform.system().lower()
            if 'windows' in OSName:
                subprocess.call(f"setx S3CLI_AWS_USER_CONFIG {path}")
            else:
                # should work on mac/linux
                subprocess.call(f"export S3CLI_AWS_USER_CONFIG={path}")

            click.echo(f"""
            'S3CLI_AWS_USER_CONFIG' set to {path}
            you must close & reopen your terminal for the changes to take effect
            """)
        except:
            click.echo(f"Unable to set variable `S3CLI_AWS_USER_CONFIG` please report this error and/or set it manually")

    else:
        click.echo(f"Invalid Path: '{path}'")


### ALL BUCKETS

@main.command()
@click.option('--unit', prompt=True, type=click.Choice(
    ['byte', 'Kb', 'Mb', 'Gb', 'Tb'], case_sensitive=False)
)
def show_table(unit):
    """
    \b
    Lists all of the s3 buckets and their metrics in a tabluar form
    Ex: `python s3Rev show-table --unit=Mb`
    """
    cli_client = s3Reviewer()


    click.echo("S3 Bucket Detail:")
    if not cli_client.showDetails(unit=unit):
        click.echo("Error rendering Bucket Detail table")

@main.command()
@click.argument('path')
@click.option('--unit', prompt=True, type=click.Choice(
    ['byte', 'Kb', 'Mb', 'Gb', 'Tb'], case_sensitive=False)
)
def save_table(path, unit):
    """
    \b
    Saves all of the s3 buckets and their metrics to an excel or csv
    Ex: `python s3Rev save-table SAVE_AS_PATH.csv|.xlsx --unit=Mb`
    """
    cli_client = s3Reviewer()
    if cli_client.saveDetailTable(path=path, unit=unit):
        click.echo(f"Bucket details saved to {path}")
    else:
        click.echo(f"Error saving bucket details to {path}")


@main.command()
def list_buckets():
    """
    \b
    Lists all accessible s3 buckets
    Ex: `python s3Rev list-buckets`
    """
    cli_client = s3Reviewer()
    print("Authorized user on the followng buckets:")
    for bucket in cli_client.list:
        click.echo(f"> {bucket}")


### SINGLE BUCKETS

@main.command()
@click.option('--bucket', prompt=True)
@click.option('--unit', prompt=True, type=click.Choice(
    ['byte', 'Kb', 'Mb', 'Gb', 'Tb'], case_sensitive=False)
)
def bucket_details(bucket, unit):
    """
    \b
    Gets the details for the provided bucket
    Ex: `python s3rev bucket-details --bucket=BUCKETNAME --unit=mb`
    """
    cli_client = s3Reviewer()

    if bucket not in cli_client.list:
        closest_matches = get_close_matches(bucket, cli_client.list, cutoff=.4)
        if len(closest_matches) == 0:
            click.echo(f"\n'{bucket}' not found, consider using the 'list-buckets' command to browse for the target bucket")
        else:
            click.echo(f"\n'{bucket}' not found did you mean one of the following:")
            for bucket in closest_matches:
                click.echo(f"> {bucket}")
        
    else:
        click.echo(cli_client.getBucket(bucket).details(unit=unit, asString=True))

if __name__ == "__main__":
    main()

    
