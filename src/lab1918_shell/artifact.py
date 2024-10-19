import click
import json

from lab1918_shell.config import Config
from lab1918_shell.client import ArtifactClient
from lab1918_shell.logger import logger

from collections import namedtuple
from tabulate import tabulate


@click.group(
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]}
)
@click.pass_context
def artifact(ctx):
    ctx.obj["client"] = ArtifactClient()


@artifact.command()
@click.pass_context
@click.option("--artifact-id", help="artifact id")
@click.option("--format", type=click.Choice(["json", "table"]), default="table")
def list(ctx, artifact_id, format):
    client: ArtifactClient = ctx.obj["client"]
    logger.info("list artifacs ...")
    try:
        if artifact_id:
            res = client.get_artifact(artifact_id)
        else:
            res = client.get_all_artifacts()
        res.raise_for_status()
        if format == "json":
            click.echo(json.dumps(res.json(), indent=4))
            return
        headers = [
            "owner",
            "file_name",
            "artifact_type",
            "version",
            "storage",
            "vendor",
            "arch",
        ]
        Row = namedtuple("Row", headers)
        tbl = []
        for each in res.json():
            row = Row(
                owner=each["owner"]["S"],
                file_name=each["file_name"]["S"],
                artifact_type=each["artifact_type"]["S"],
                version=each["file_version"]["S"],
                storage=each["storage"]["S"],
                vendor=each["vendor"]["S"],
                arch=each.get("arch", {}).get("S", "x86"),
            )
            tbl.append(row)
        hdrs = [each.replace("_", "-") for each in headers]
        click.echo(tabulate(tbl, hdrs, tablefmt="fancy_grid"))
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@artifact.command()
@click.pass_context
@click.option("--file-name", help="file name")
@click.option("--file-version", help="file version", type=click.STRING)
@click.option(
    "--vendor", help="vendor", type=click.Choice(["arista", "cisco", "nokia"])
)
@click.option(
    "--artifact-type",
    type=click.Choice(["qcow", "vmdk", "container"]),
    default="container",
)
@click.option("--storage", type=click.Choice(["s3", "docker"]), default="s3")
def create(ctx, file_name, file_version, vendor, artifact_type, storage):
    client: ArtifactClient = ctx.obj["client"]
    logger.info("create artifact ...")
    try:
        res = client.create_artifact(
            file_name, file_version, vendor, artifact_type, storage
        )
        res.raise_for_status()
        click.echo(f"created artifact {file_name}")
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@artifact.command()
@click.pass_context
@click.option("--artifact-id", help="artifact id")
def delete(ctx, artifact_id):
    client: ArtifactClient = ctx.obj["client"]
    logger.info("delete artifact ...")
    try:
        res = client.delete_artifact(artifact_id)
        res.raise_for_status()
        click.echo(f"deleted artifact {artifact_id}")
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


def main():
    config = Config()
    default = config.get_config(profile="default")
    if default["api_key"] == "<replace with api key>":
        logger.error("config proper api key at ~/.lab1918/shell.ini!")
    else:
        artifact(obj={})


if __name__ == "__main__":
    main()
