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
@click.option("--topology-id", help="topology id")
def list(ctx, topology_id):
    client = ctx.obj["client"]
    logger.info("list topologies ...")
    try:
        if topology_id:
            res = client.get_topology(topology_id)
        else:
            res = client.get_all_topologies()
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except Exception as e:
        click.echo(f"failed to create topology: {e}", err=True)


@topology.command()
@click.pass_context
@click.option("--topology-id", help="topology id")
def delete(ctx, topology_id):
    client = ctx.obj["client"]
    logger.info("delete topology ...")
    try:
        res = client.delete_topology(topology_id)
        res.raise_for_status()
        click.echo(f"deleted topology {topology_id}")
    except Exception as e:
        click.echo(f"failed to delete topology: {e}", err=True)


@topology.command()
@click.pass_context
@click.option("--topology-id", help="topology id")
@click.option("--topology-name", help="topology name")
def update(ctx, topology_id, topology_name):
    client = ctx.obj["client"]
    logger.info("update topology ...")
    try:
        res = client.update_topology(topology_id, topology_name)
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except Exception as e:
        click.echo(f"failed to update topology: {e}", err=True)


def main():
    config = Config()
    default = config.get_config(profile="default")
    if default["api_key"] == "<replace with api key>":
        logger.error("config proper api key at ~/.lab1918/shell.ini!")
    else:
        topology(obj={})


if __name__ == "__main__":
    main()
