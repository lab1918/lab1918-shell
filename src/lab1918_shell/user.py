import click
import json

from lab1918_shell.config import Config
from lab1918_shell.client import User
from lab1918_shell.logger import logger

from collections import namedtuple
from tabulate import tabulate
from requests import Response
from typing import Tuple, List


def get_user_table(response: Response) -> Tuple[List, List]:
    tbl = []
    hdrs = ["setting", "value"]
    Row = namedtuple("Row", hdrs)
    for key, value in response.json().items():
        row = Row(setting=key.replace("_", "-"), value=value)
        tbl.append(row)
    return hdrs, tbl


@click.group(
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]}
)
@click.pass_context
def user(ctx):
    ctx.obj["client"] = User()


@user.command()
@click.pass_context
@click.option("--format", type=click.Choice(["json", "table"]), default="table")
def list(ctx, format):
    client: User = ctx.obj["client"]
    logger.info("whoami ...")
    try:
        res = client.whoami()
        res.raise_for_status()
        if format == "json":
            click.echo(json.dumps(res.json(), indent=4))
        else:
            headers, table = get_user_table(res)
            click.echo(tabulate(table, headers, tablefmt="fancy_grid"))
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@user.command()
@click.pass_context
@click.option("--aws-region", help="aws region, for example us-east-1")
@click.option(
    "--aws-ami-id",
    help="aws ami, must be valid for giving aws region, for example ami-0e879a1b306fffb22",
)
@click.option("--aws-instance-size", help="ec2 instance type, example t4g.small")
@click.option(
    "--aws-reservation-size",
    help="reservation size, default is one ec2",
    type=click.IntRange(min=1, max=128),
)
def update(
    ctx,
    aws_region,
    aws_ami_id,
    aws_instance_size,
    aws_reservation_size,
):
    client: User = ctx.obj["client"]
    logger.info("change user setting ...")
    try:
        res = client.whoami()
        res.raise_for_status()
        user = res.json()
        new_setting = {"user_id": user["user_id"]}
        if aws_region:
            new_setting["aws_region"] = aws_region
        if aws_ami_id:
            new_setting["aws_ami_id"] = aws_ami_id
        if aws_instance_size:
            new_setting["aws_instance_size"] = aws_instance_size
        if aws_reservation_size:
            new_setting["aws_reservation_size"] = aws_reservation_size
        result = client.update(new_setting)
        result.raise_for_status()
        headers, table = get_user_table(result)
        click.echo(tabulate(table, headers, tablefmt="fancy_grid"))
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


def main():
    config = Config()
    default = config.get_config(profile="default")
    if default["api_key"] == "<replace with api key>":
        logger.error("config proper api key at ~/.lab1918/shell.ini!")
    else:
        user(obj={})


if __name__ == "__main__":
    main()
