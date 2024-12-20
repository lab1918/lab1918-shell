import click
import json
import yaml

from lab1918_shell.config import Config
from lab1918_shell.client import TopologyClient
from lab1918_shell.logger import logger

from collections import namedtuple
from tabulate import tabulate
from operator import attrgetter


@click.group(
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]}
)
@click.pass_context
def topology(ctx):
    ctx.obj["client"] = TopologyClient()


@topology.command()
@click.pass_context
@click.option("--topology-name", help="topology name")
def create(ctx, topology_name):
    client: TopologyClient = ctx.obj["client"]
    logger.info("create topology ...")
    try:
        res = client.create_topology(topology_name)
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@topology.command()
@click.pass_context
@click.option("--topology-id", "-t", help="topology id")
@click.option("--format", type=click.Choice(["json", "table"]), default="table")
@click.option("--config", is_flag=True, help="only display topology config")
@click.option("--status", is_flag=True, help="only display topology status")
@click.option("--reservation", is_flag=True, help="only display reservation")
@click.option("--workflow", is_flag=True, help="only display workflow")
def list(ctx, topology_id, format, config, status, reservation, workflow):
    client: TopologyClient = ctx.obj["client"]
    logger.info("list topologies ...")
    try:
        if topology_id:
            res = client.get_topology(topology_id)
        else:
            res = client.get_all_topologies()
        res.raise_for_status()
        if format == "json" or config or status or reservation:
            if config:
                result = [
                    json.loads(each.get("topology_config", {}).get("S", "{}"))
                    for each in res.json()
                ]
            elif status:
                result = [
                    json.loads(each.get("topology_status", {}).get("S", "{}"))
                    for each in res.json()
                ]
            elif reservation:
                result = [each.get("reservation", {}) for each in res.json()]
            else:
                result = res.json()
            click.echo(json.dumps(result, indent=4))
            return
        if workflow:
            headers = [
                "topology_id",
                "workflow_name",
                "workflow_id",
                "started_at",
                "finished",
            ]
            Row = namedtuple("Row", headers)
            tbl = []
            for topology in res.json():
                topology_id = topology["topology_id"]["S"]
                workflows = topology.get("workflows", {}).get("L", [])
                workflow = topology.get("workflow", {})
                if workflow is not None:
                    workflows.append(workflow)
                for each in workflows:
                    row = Row(
                        topology_id=topology_id,
                        workflow_name=each["M"]["workflow_name"]["S"],
                        workflow_id=each["M"]["workflow_id"]["S"],
                        started_at=each["M"]["started_at"]["S"][:19],
                        finished=each["M"]["finished"]["BOOL"],
                    )
                    tbl.append(row)
            hdrs = [each.replace("_", "-") for each in headers]
            click.echo(
                tabulate(
                    sorted(tbl, key=attrgetter("started_at"), reverse=True),
                    hdrs,
                    tablefmt="fancy_grid",
                )
            )
            return
        headers = [
            "name",
            "owner",
            "topology_id",
            "workflow",
            "reservation",
            "deployed",
            "version",
        ]
        Row = namedtuple("Row", headers)
        tbl = []
        for each in res.json():
            if not each.get("workflow"):
                workflow_status = None
            elif (
                each.get("workflow", {}).get("M", {}).get("finished", {}).get("BOOL")
                is True
            ):
                workflow_status = "finished"
            else:
                workflow_status = "running"
            row = Row(
                name=each["topology_name"]["S"],
                owner=each["owner"]["S"],
                topology_id=each["topology_id"]["S"],
                workflow=each.get("workflow", {})
                .get("M", {})
                .get("workflow_name", {})
                .get("S", "None")
                + f"({workflow_status})",
                reservation=bool(each.get("reservation")),
                deployed=each.get("deployed", {}).get("BOOL", False),
                version=each["version"]["N"],
            )
            tbl.append(row)
        hdrs = [each.replace("_", "-") for each in headers]
        click.echo(tabulate(tbl, hdrs, tablefmt="fancy_grid"))
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@topology.command()
@click.pass_context
@click.option("--topology-id", "-t", help="topology id")
def delete(ctx, topology_id):
    client: TopologyClient = ctx.obj["client"]
    logger.info("delete topology ...")
    try:
        res = client.delete_topology(topology_id)
        res.raise_for_status()
        click.echo(f"deleted topology {topology_id}")
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@topology.command()
@click.pass_context
@click.option("--topology-id", "-t", help="topology id")
@click.option("--topology-json", help="topology config json file name")
@click.option("--topology-yaml", help="topology config yaml file name")
def update(ctx, topology_id, topology_json, topology_yaml):
    client: TopologyClient = ctx.obj["client"]
    logger.info("update topology ...")
    try:
        if topology_json:
            with open(topology_json) as f:
                config = json.loads(f.read())
        elif topology_yaml:
            with open(topology_yaml) as stream:
                config = yaml.safe_load(stream)
        else:
            click.echo("please specify either topology-json or topology-yaml")
            return
        res = client.update_topology(topology_id, config)
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except yaml.YAMLError as e:
        click.echo(e, err=True)
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@topology.command()
@click.pass_context
@click.option("--topology-id", "-t", help="topology id")
@click.option(
    "--extra-args",
    help="extra args for topology reservation, use key=value format",
    multiple=True,
)
def reserve(ctx, topology_id, extra_args):
    client: TopologyClient = ctx.obj["client"]
    logger.info("reserve topology ...")
    kwargs = {}
    if extra_args:
        for each_arg in extra_args:
            key, value = each_arg.split("=")
            key = key.replace("-", "_")
            kwargs[key] = value
    try:
        res = client.reserve(topology_id, kwargs)
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@topology.command()
@click.pass_context
@click.option("--topology-id", "-t", help="topology id")
@click.option("--reservation-id", help="reservation id")
@click.option("--account-id", help="account id")
@click.option("--force", is_flag=True, help="release resource with force")
def release(ctx, topology_id, reservation_id, account_id, force):
    client: TopologyClient = ctx.obj["client"]
    logger.info("release topology ...")
    try:
        res = client.release(topology_id, reservation_id, account_id, force)
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@topology.command()
@click.pass_context
@click.option("--topology-id", "-t", help="topology id")
@click.option("--dry-run", is_flag=True, help="dry run deployment")
def deploy(ctx, topology_id, dry_run):
    client: TopologyClient = ctx.obj["client"]
    logger.info("deploy topology ...")
    try:
        res = client.deploy(topology_id, dry_run)
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@topology.command()
@click.pass_context
@click.option("--topology-id", "-t", help="topology id")
@click.option("--dry-run", is_flag=True, help="dry run undeployment")
def undeploy(ctx, topology_id, dry_run):
    client: TopologyClient = ctx.obj["client"]
    logger.info("undeploy topology ...")
    try:
        res = client.undeploy(topology_id, dry_run)
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@topology.command()
@click.pass_context
@click.option("--topology-id", "-t", help="topology id")
def ping(ctx, topology_id):
    client: TopologyClient = ctx.obj["client"]
    logger.info("ping topology ...")
    try:
        res = client.ping(topology_id)
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except Exception as e:
        click.echo(e, err=True)
        click.echo(f"{e.response.json()}", err=True)


@topology.command()
@click.pass_context
@click.option("--topology-id", "-t", help="topology id")
@click.option(
    "--params", help="json string workflow input", default="{}", show_default=True
)
def bootstrap(ctx, topology_id, params):
    client: TopologyClient = ctx.obj["client"]
    logger.info(
        f"run bootstrap workflow for topology {topology_id} with extra params {params} ..."
    )
    try:
        res = client.bootstrap(topology_id, params)
        res.raise_for_status()
        click.echo(json.dumps(res.json(), indent=4))
    except Exception as e:
        click.echo(f"{e}", err=True)
        click.echo(f"{e.response.json()}", err=True)


def main():
    config = Config()
    default = config.get_config(profile="default")
    if default["api_key"] == "<replace with api key>":
        logger.error("config proper api key at ~/.lab1918/shell.ini!")
    else:
        topology(obj={})


if __name__ == "__main__":
    main()
