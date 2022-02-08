import click

def info(msg):
    click.echo(msg, file=config.OUTPUT_LOCATION_WRITE)

def error(msg):
