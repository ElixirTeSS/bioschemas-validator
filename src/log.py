import click
import src.Classes.config as config


def stdout(msg):
    click.echo(msg)


def info(msg):
    click.echo(msg, file=config.OUTPUT_LOCATION_WRITE)


def error(msg):
    click.echo(msg, fg="red", file=config.OUTPUT_LOCATION_WRITE)
