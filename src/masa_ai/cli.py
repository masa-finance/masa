import click
from masa_ai.masa import Masa

@click.group()
def main():
    """
    The main entry point for the masa-ai-cli command.
    """
    pass

@main.command()
@click.argument('json_file', required=False, type=click.Path(exists=True))
def process(json_file):
    """
    Process all requests (both resumed and new).

    Optionally, provide a JSON_FILE containing requests to process.
    """
    masa = Masa()
    masa.process_requests(json_file)

@main.command()
@click.argument('page', required=False)
def docs(page):
    """
    Rebuild and view the documentation.

    Optionally, specify a PAGE to view a specific documentation page.
    """
    masa = Masa()
    masa.view_docs(page)

@main.command()
def data():
    """
    List the scraped data files based on the configured data directory.
    """
    masa = Masa()
    masa.list_scraped_data()

@main.group()
def config():
    """
    Manage configurations in settings.yaml.
    """
    pass

@config.command('get', help="""
Get the value of a configuration KEY.

\b
Example:
  masa-ai-cli config get default.twitter.BASE_URL

This command retrieves the value of the specified configuration key from settings.yaml.
""")
@click.argument('key')
def config_get(key):
    """
    Get the value of a configuration KEY.
    """
    masa = Masa()
    value = masa.get_config(key)
    click.echo(f"{key} = {value}")

@config.command('set', help="""
Set the VALUE of a configuration KEY.

\b
Example:
  \033[92mmasa-ai-cli config set default.twitter.BASE_URL "https://api.twitter.com/"\033[0m

This command sets the specified configuration key to the provided value in settings.yaml.
""")
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """
    Set the VALUE of a configuration KEY.
    """
    masa = Masa()
    masa.set_config(key, value)
    click.echo(f"Set {key} to {value}")

if __name__ == '__main__':
    main()
