import click
import json

from lab1918_shell.config import Config
from lab1918_shell.client import User
from lab1918_shell.logger import logger

from collections import namedtuple
from tabulate import tabulate


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
    logger.info("who am i ...")
    try:
        res = client.whoami()
        res.raise_for_status()
        if format == "json":
            click.echo(json.dumps(res.json(), indent=4))
        else:
            tbl = []
            headers = ["setting", "value"]
            Row = namedtuple("Row", headers)
            for key, value in res.json().items():
                row = Row(setting=key, value=value)
                tbl.append(row)
            click.echo(tabulate(tbl, headers, tablefmt="fancy_grid"))
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
