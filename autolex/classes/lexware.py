"""Lexware API client classes.

This module provides classes for interacting with the Lexware API, handling webhooks,
and managing company, billing, shipping, and contact person data.
"""

import json

from base64 import b64decode
from dataclasses import dataclass

import requests

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from flask import Request


@dataclass
class Webhook:
    """Represents a webhook event with details such as organization ID, event type, resource ID, and event date."""
    organizationId: str
    eventType: str
    resourceId: str
    eventDate: str

    @classmethod
    def from_dict(cls: 'Webhook', data: dict) -> 'Webhook':
        """Create a Webhook instance from a dictionary of data.

        :param data: A dictionary containing webhook data.
        :return: A Webhook instance.
        """
        return cls(
            organizationId=data.get('organizationId'),
            eventType=data.get('eventType'),
            resourceId=data.get('resourceId'),
            eventDate=data.get('eventDate')
        )

    @classmethod
    def load_webhook(cls: 'Webhook', flask_request: Request, pubkey_path: str) -> None:
        """Load webhook data from a Flask request object.

        :param flask_request: A Flask request object containing webhook data.
        """
        # Check the signature
        signature = flask_request.headers.get('X-Lxo-Signature')
        public_key = open(pubkey_path).read()
        if not cls._verify_sha512_signature(public_key, signature, json.dumps(flask_request.json)):
            raise ValueError('Invalid signature')

        # Load the webhook data
        data = flask_request.json

        return cls.from_dict(data)

    @staticmethod
    def _verify_sha512_signature(public_key: str, signature: str, data: str) -> bool:
        """Verify a SHA-512 signature using a public key.

        :param public_key: The public key used to verify the signature.
        :param signature: The signature to verify.
        :param data: The data to verify.
        :return: True if the signature is valid, False otherwise.
        """
        # Replace remove spaces from data
        data = data.replace(' ', '')

        # Verify the signature
        key = RSA.import_key(public_key)
        h = SHA512.new(data.encode())
        verifier = PKCS1_v1_5.new(key)
        return verifier.verify(h, b64decode(signature.encode()))


@dataclass
class BillingData:
    """Represents billing data with attributes such as street, zip, city, and country code."""
    street: str
    zip: str
    city: str
    countryCode: str

    @classmethod
    def from_dict(cls: 'BillingData', data: dict) -> 'BillingData':
        """Create a BillingData instance from a dictionary of data.

        :param data: A dictionary containing billing data.
        :return: A BillingData instance.
        """
        return cls(
            street=data.get('street'),
            zip=data.get('zip'),
            city=data.get('city'),
            countryCode=data.get('countryCode')
        )


@dataclass
class ShippingData:
    """Represents shipping data with attributes such as street, zip, city, and country code."""
    street: str
    zip: str
    city: str
    countryCode: str

    @classmethod
    def from_dict(cls: 'ShippingData', data: dict) -> 'ShippingData':
        """Create a ShippingData instance from a dictionary of data.

        :param data: A dictionary containing shipping data.
        :return: A ShippingData instance.
        """
        return cls(
            street=data.get('street'),
            zip=data.get('zip'),
            city=data.get('city'),
            countryCode=data.get('countryCode')
        )


@dataclass
class ContactPerson:
    """Contact person data.

    Represents a contact person with attributes such as salutation, first name, last name, primary status,
    email address, and phone number.
    """
    salutation: str
    firstName: str
    lastName: str
    primary: bool
    emailAddress: str
    phoneNumber: str

    @classmethod
    def from_dict(cls: 'ContactPerson', data: dict) -> 'ContactPerson':
        """Create a ContactPerson instance from a dictionary of data.

        :param data: A dictionary containing contact person data.
        :return: A ContactPerson instance.
        """
        return cls(
            salutation=data.get('salutation'),
            firstName=data.get('firstName'),
            lastName=data.get('lastName'),
            primary=data.get('primary'),
            emailAddress=data.get('emailAddress'),
            phoneNumber=data.get('phoneNumber')
        )


@dataclass
class Company:
    """Represents a company with various attributes such as id, organizationId, version, roles.

    Company details, addresses, email addresses, phone numbers, xRechnung, note, and archived status.
    """
    id: str
    organizationId: str
    version: int
    roles: dict
    name: str
    taxNumber: str
    vatId: str
    allowTaxFreeInvoices: bool
    contactPersons: list[ContactPerson]
    emailAddresses: list[str]
    phoneNumbers: list[str]
    faxNumbers: list[str]
    xRechnung: dict
    note: str
    archived: bool
    billing_adresses: list[BillingData]
    shipping_adresses: list[ShippingData]

    @classmethod
    def from_dict(cls: 'Company', data: dict) -> 'Company':
        """Create a Company instance from a dictionary of data.

        :param data: A dictionary containing company data.
        :return: A Company instance.
        """
        return cls(
            id=data.get('id'),
            organizationId=data.get('organizationId'),
            version=data.get('version'),
            roles=data.get('roles'),
            name=data.get('company', {}).get('name'),
            taxNumber=data.get('company', {}).get('taxNumber'),
            vatId=data.get('company', {}).get('vatRegistrationId'),
            allowTaxFreeInvoices=data.get('company', {}).get('allowTaxFreeInvoices'),
            contactPersons=[
                ContactPerson.from_dict(cp) for cp in data.get('company', {}).get('contactPersons', [])
            ],
            emailAddresses=data.get('emailAddresses', []),
            phoneNumbers=data.get('phoneNumbers', {}).get('business', []),
            faxNumbers=data.get('phoneNumbers', {}).get('fax', []),
            xRechnung=data.get('xRechnung', {}),
            note=data.get('note', ''),
            archived=data.get('archived', False),
            billing_adresses=[
                BillingData.from_dict(addr) for addr in data.get('addresses', {}).get('billing', [])
            ],
            shipping_adresses=[
                ShippingData.from_dict(addr) for addr in data.get('addresses', {}).get('shipping', [])
            ]
        )


class Lexware(requests.Session):
    """A client class for interacting with the Lexware API."""
    def __init__(self: 'Lexware', base_url: str, api_key: str) -> None:
        """Initialize the Lexware client.

        :param base_url: The base URL of the Lexware API.
        :param api_key: The API key for authentication.
        """
        super().__init__()
        self.base_url = base_url
        self.headers.update({'Authorization': f'Bearer {api_key}'})

    def get_contact(self: 'Lexware', id: str) -> Company:
        """Retrieve a contact by ID.

        :param id: The ID of the contact.
        :return: A Company instance representing the contact.
        """
        response = self.get(f'{self.base_url}/contacts/{id}')
        response.raise_for_status()

        data = response.json()

        if 'company' in data:
            return Company.from_dict(data)
