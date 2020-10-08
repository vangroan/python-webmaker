import click


@click.group()
def main():
    pass


@main.command()
@click.option('--log-level', '-l')
def build(log_level):
    """
    Generates the site.
    """
    click.echo(click.style('Hello World!', fg='green'))
    click.echo(click.style('Some more text', bg='blue', fg='white'))
    click.echo(click.style('ATTENTION', blink=True, bold=True))
    click.secho('Hello World!', fg='green')
    click.secho('Some more text', bg='blue', fg='white')
    click.secho('ATTENTION', blink=True, bold=True)
    click.secho('⠯', fg='green')


@main.command()
def clean():
    """
    Deletes the output directory.
    """
    click.echo('Clean')
