import click
import os
import json
from masa_ai.masa import Masa
from click import style

@click.group()
def main():
    """
    The main entry point for the masa-ai-cli command.
    """
    pass

@main.command()
@click.argument('input', required=False)
def process(input):
    """
    Process requests from a JSON file, a JSON string, a list of requests, or a single request.

    \b
    INPUT can be:
    - A path to a JSON file containing requests.
    - A JSON string representing a single request or a list of requests.
    - Omitted to process existing or default requests.
    """
    masa = Masa()

    if input:
        # Attempt to interpret the input
        if os.path.isfile(input):
            # If input is a file path
            masa.process_requests(input)
        else:
            try:
                # Try to parse the input as JSON
                requests = json.loads(input)
                masa.process_requests(requests)
            except json.JSONDecodeError:
                message = "Invalid input. Please provide a valid JSON file path or a JSON string representing requests."
                click.echo(style(message, fg='red'))
                masa.qc_manager.log_error(message, context="CLI")
                return
    else:
        # No input provided, process default or existing requests
        masa.process_requests()

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
    message = f"{key} = {value}"
    # click.echo(style(message, fg='green'))
    masa.qc_manager.log_info(message, context="CLI")

@config.command('set', help="""
Set the VALUE of a configuration KEY.

\b
Example:
  masa-ai-cli config set default.twitter.BASE_URL "https://api.twitter.com/"

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
    message = f"Set {key} to {value}"
    click.echo(style(message, fg='green'))
    masa.qc_manager.log_info(message, context="CLI")

@main.command()
@click.option('--statuses', default='queued,in_progress', help='Comma-separated list of statuses to filter requests.')
def list_requests(statuses):
    """
    List requests filtered by statuses.

    \b
    STATUS can be:
    - queued
    - in_progress
    - completed
    - failed
    - cancelled
    - all

    By default, it lists requests with statuses 'queued' and 'in_progress'.
    """
    masa = Masa()
    statuses_list = statuses.split(',') if statuses != 'all' else None
    masa.list_requests(statuses_list)

@main.command()
@click.argument('request_ids', required=False)
def clear_requests(request_ids):
    """
    Clear queued or in-progress requests.

    \b
    REQUEST_IDS can be:
    - A comma-separated list of request IDs to clear.
    - Omitted to clear all queued and in-progress requests.
    """
    masa = Masa()
    request_ids_list = request_ids.split(',') if request_ids else None
    masa.clear_requests(request_ids_list)

if __name__ == '__main__':
    main()