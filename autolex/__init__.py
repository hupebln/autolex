import os

import click

from flask import Flask, request

from autolex.classes.autotask import AutoTask
from autolex.classes.lexware import Lexware, Webhook


app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook() -> str | None:
    """Handle incoming webhook POST requests."""
    if request.method == 'POST':
        data = request.json
        webhook = Webhook.from_dict(data)
        return "Webhook received!"

@click.group()
def cli() -> None:
    """Command Line Interface entry point."""
    pass

@click.command('runserver')
@click.option('--host', default='0.0.0.0', type=str, help='the hostname to listen on')
@click.option('--port', default=8000, type=int, help='the port of the webserver')
def start_server(host: str, port: int) -> None:
    """Start the Flask web server."""
    app.run(host=host, port=port)

@click.command()
@click.option('--contact-id', type=str, help='the ID of the contact to synchronize')
def sync(contact_id: str) -> None:
    """Synchronize data with Lexware."""
    lex_base_url = os.getenv('LEXOFFICE_BASE_URL')
    lex_api_key = os.getenv('LEXOFFICE_API_KEY')

    auto_base_url = os.getenv('AUTOTASK_BASE_URL')
    auto_api_user = os.getenv('AUTOTASK_API_USERNAME')
    auto_api_key = os.getenv('AUTOTASK_API_SECRET')
    auto_integration_code = os.getenv('AUTOTASK_API_INTEGRATION_CODE')
    auto_owner_resource_id = os.getenv('AUTOTASK_OWNER_RESOURCE_ID')

    # Create the Lexware and AutoTask clients
    lexware = Lexware(lex_base_url, lex_api_key)
    autotask = AutoTask(auto_base_url, auto_api_user, auto_api_key, auto_integration_code, int(auto_owner_resource_id))

    # Get the contact from Lexware and create a company in AutoTask
    if contact_id:
        lex_company = lexware.get_contact(contact_id)
        autotask.create_company(lex_company)
        return

cli.add_command(start_server)
cli.add_command(sync)


if __name__ == '__main__':
    cli()
