import click
import json

from lab1918_shell.config import Config
from lab1918_shell.client import TopologyClient
from lab1918_shell.logger import logger

from collections import namedtuple
from tabulate import tabulate


@click.group()
@click.pass_context
def topology(ctx):
    ctx.obj["client"] = TopologyClient()


@topology.command()
@click.pass_context
@click.option("--topology-name", help="topology name")
def create(ctx, topology_name):
    client = ctx.obj["client"]
    logger.info("create topology ...")
    try:
        res = client.create_topology(topology_name)
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except Exception as e:
        click.echo(f"failed to create topology: {e}", err=True)


@topology.command()
@click.pass_context
def list(ctx):
    client = ctx.obj["client"]
    logger.info("list all topologies ...")
    try:
        res = client.get_all_topologies()
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except Exception as e:
        click.echo(f"failed to create topology: {e}", err=True)


def main():
    config = Config()
    default = config.get_config(profile="default")
    if default["api_key"] == "<replace with api key>":
        logger.error("config proper api key at ~/.lab1918/shell.ini!")
    else:
        topology(obj={})


if __name__ == "__main__":
    main()
