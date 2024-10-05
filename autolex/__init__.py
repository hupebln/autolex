import logging
import os

import click

from flask import Flask, request

from autolex.classes.autotask import AutoTask
from autolex.classes.lexware import Lexware, Webhook


# Set up logging
logging_level = os.getenv('LOGGING_LEVEL', 'INFO')
logging_num_level = logging.getLevelNamesMapping().get(logging_level, logging.INFO)
logging.basicConfig(level=logging_num_level)

# Create a logger
logger = logging.getLogger('autolex')


app = Flask(__name__)


def _return_clients() -> tuple[Lexware, AutoTask]:
    """Create and return Lexware and AutoTask clients."""
    logger.debug('Creating Lexware and AutoTask clients...')

    # Get the environment variables
    lex_base_url = os.getenv('LEXOFFICE_BASE_URL')
    lex_api_key = os.getenv('LEXOFFICE_API_KEY')

    auto_base_url = os.getenv('AUTOTASK_BASE_URL')
    auto_api_user = os.getenv('AUTOTASK_API_USERNAME')
    auto_api_key = os.getenv('AUTOTASK_API_SECRET')
    auto_integration_code = os.getenv('AUTOTASK_API_INTEGRATION_CODE')
    auto_owner_resource_id = os.getenv('AUTOTASK_OWNER_RESOURCE_ID')
    auto_default_phone = os.getenv('AUTOTASK_DEFAULT_PHONE')

    # Create the Lexware and AutoTask clients
    lexware = Lexware(
        base_url=lex_base_url,
        api_key=lex_api_key
    )
    autotask = AutoTask(
        base_url=auto_base_url,
        api_user=auto_api_user,
        api_key=auto_api_key,
        api_integration_code=auto_integration_code,
        owner_resource_id=int(auto_owner_resource_id),
        default_phone=auto_default_phone
    )

    return lexware, autotask

@app.route('/webhook', methods=['POST'])
def webhook() -> str | None:
    """Handle incoming webhook POST requests."""
    logger.debug('Received webhook request...')

    if request.method == 'POST':
        webhook: Webhook = Webhook.load_webhook(request, os.getenv('LEXOFFICE_PUBKEY_PATH'))

        # Get the contact ID from the webhook
        contact_id = webhook.resourceId
        logger.info(f'Webhook received for contact ID: {contact_id}')

        # Get the Lexware and AutoTask clients
        lexware, autotask = _return_clients()

        def _sync_contact() -> None:
            # Handle the webhook event
                lex_company = lexware.get_contact(contact_id)
                autotask.assure_company(lex_company)

        match webhook.eventType:
            case 'contact.created':
                _sync_contact()
                logger.info(f'Contact ID: {contact_id} has been created.')
                return "Webhook received!"
            case 'contact.changed':
                _sync_contact()
                logger.info(f'Contact ID: {contact_id} has been updated.')
                return "Webhook received!"
            case _:
                logger.warning(f'Unhandled webhook event type: {webhook.eventType}')
                return "Webhook received, but not processed!"

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
    # Get the Lexware and AutoTask clients
    lexware, autotask = _return_clients()

    # Get the contact from Lexware and create a company in AutoTask
    if contact_id:
        lex_company = lexware.get_contact(contact_id)
        autotask.create_company(lex_company)
        return

cli.add_command(start_server)
cli.add_command(sync)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
