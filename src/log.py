import click
import src.Classes.config as config


def stdout(msg):
    click.secho(msg)


def info(msg):
    click.secho(msg, file=config.OUTPUT_LOCATION_WRITE)


def success(msg):
    click.secho(msg, fg='green', file=config.OUTPUT_LOCATION_WRITE)


def warn(msg):
    click.secho(msg, fg='yellow', file=config.OUTPUT_LOCATION_WRITE)


def error(msg):
    click.secho(msg, fg='red', file=config.OUTPUT_LOCATION_WRITE)
