"""This module contains classes for handling AutoTask requests and representing companies."""

import logging

from dataclasses import asdict, dataclass, field
from typing import Dict, List
from urllib.parse import quote

import requests

from autolex.classes.lexware import Company as LexCompany
from autolex.classes.lexware import ContactPerson as LexContactPerson


logger = logging.getLogger('autolex.autotask')


@dataclass
class Company:
    """Represents a company with various attributes."""
    id: int = None
    additionalAddressInformation: str = None
    address1: str = None
    address2: str = None
    alternatePhone1: str = None
    alternatePhone2: str = None
    apiVendorID: int = None
    assetValue: int = None
    billToCompanyLocationID: int = None
    billToAdditionalAddressInformation: str = None
    billingAddress1: str = None
    billingAddress2: str = None
    billToAddressToUse: int = None
    billToAttention: str = None
    billToCity: str = None
    billToCountryID: int = None
    billToState: str = None
    billToZipCode: str = None
    city: str = None
    classification: int = None
    companyCategoryID: int = None
    companyName: str = None
    companyNumber: str = None
    companyType: int = 1
    competitorID: int = None
    countryID: int = None
    createDate: str = None
    createdByResourceID: int = None
    currencyID: int = None
    fax: str = None
    impersonatorCreatorResourceID: int = None
    invoiceEmailMessageID: int = None
    invoiceMethod: int = None
    invoiceNonContractItemsToParentCompany: bool = None
    invoiceTemplateID: int = None
    isActive: bool = None
    isClientPortalActive: bool = None
    isEnabledForComanaged: bool = None
    isSample: bool = None
    isTaskFireActive: bool = None
    isTaxExempt: bool = None
    lastActivityDate: str = None
    lastTrackedModifiedDateTime: str = None
    marketSegmentID: int = None
    ownerResourceID: int = None
    parentCompanyID: int = None
    phone: str = None
    postalCode: str = None
    purchaseOrderTemplateID: int = None
    quoteEmailMessageID: int = None
    quoteTemplateID: int = None
    sicCode: str = None
    state: str = None
    stockMarket: str = None
    stockSymbol: str = None
    surveyCompanyRating: int = None
    taxID: str = None
    taxRegionID: int = None
    territoryID: int = None
    webAddress: str = None
    userDefinedFields: List[Dict[str, str]] = None

    def as_dict(self: 'Company') -> dict:
        """Return the company as a dictionary - return only attributes which are set."""
        logger.debug(f'Company as_dict: {asdict(self)}')

        obj_dict: dict = asdict(self)
        return {k: v for k, v in obj_dict.items() if v is not None}


@dataclass
class SoapParentPropertyId:
    """Represents a SOAP parent property ID."""
    body: Dict = field(default_factory=dict)


@dataclass
class UserDefinedField:
    """Represents a user-defined field with a name and value."""
    name: str = None
    value: str = None


@dataclass
class ContactModel:
    """Represents a contact model with various attributes."""
    id: int = None
    additionalAddressInformation: str = None
    addressLine: str = None
    addressLine1: str = None
    alternatePhone: str = None
    apiVendorID: int = None
    bulkEmailOptOutTime: str = None
    city: str = None
    companyID: int = None
    companyLocationID: int = None
    countryID: int = None
    createDate: str = None
    emailAddress: str = None
    emailAddress2: str = None
    emailAddress3: str = None
    extension: str = None
    externalID: str = None
    facebookUrl: str = None
    faxNumber: str = None
    firstName: str = None
    impersonatorCreatorResourceID: int = None
    isActive: int = None
    isOptedOutFromBulkEmail: bool = None
    lastActivityDate: str = None
    lastModifiedDate: str = None
    lastName: str = None
    linkedInUrl: str = None
    middleInitial: str = None
    mobilePhone: str = None
    namePrefix: int = None
    nameSuffix: int = None
    note: str = None
    receivesEmailNotifications: bool = None
    phone: str = None
    primaryContact: bool = None
    roomNumber: str = None
    solicitationOptOut: bool = None
    solicitationOptOutTime: str = None
    state: str = None
    surveyOptOut: bool = None
    title: str = None
    twitterUrl: str = None
    zipCode: str = None
    soapParentPropertyId: SoapParentPropertyId = None
    userDefinedFields: List[UserDefinedField] = None

    def as_dict(self: 'ContactModel') -> dict:
        """Return the ContactModel as a dictionary - return only attributes which are set."""
        logger.debug(f'ContactModel as_dict: {asdict(self)}')

        obj_dict: dict = asdict(self)
        return {k: v for k, v in obj_dict.items() if v is not None}


class AutoTask(requests.Session):
    """Class for handling AutoTask requests."""

    def __init__(
        self: 'AutoTask',
        base_url: str,
        api_user: str,
        api_key: str,
        api_integration_code: str,
        owner_resource_id: int,
        default_phone: str,
        default_first_name: str,
        default_last_name: str,
        overwrite_name_list: list[str] | None = None
    ) -> None:
        """Initialize the AutoTask class."""
        logger.debug('Initializing AutoTask client...')

        super().__init__()
        self.base_url = base_url
        self.api_user = api_user
        self.api_key = api_key
        self.api_integration_code = api_integration_code
        self.owner_resource_id = owner_resource_id
        self.default_phone = default_phone
        self.default_first_name = default_first_name
        self.default_last_name = default_last_name

        if overwrite_name_list is None:
            self.overwrite_name_list = []
        else:
            self.overwrite_name_list = overwrite_name_list

        self.headers = {
            'ApiIntegrationCode': self.api_integration_code,
            'UserName': self.api_user,
            'Secret': self.api_key,
        }

    def _get_country_id(self: 'AutoTask', country_code: str) -> int:
        """Get the country ID for a given country code."""
        logger.debug(f'Getting country ID for country code: {country_code}')

        quoted_search = quote(f'{{"filter": [{{"field": "countryCode", "op": "eq", "value": "{country_code}"}}]}}')
        countries_url = f"{self.base_url}/Countries/query?search={quoted_search}"
        countries = self.get(countries_url).json()

        for country in countries.get('items', []):
            if country.get('countryCode') == country_code:
                return country.get('id')

    def _create_contact_object(self: 'AutoTask', lex_contact: LexContactPerson, primary: bool) -> ContactModel:
        """Create a contact object for the AutoTask API."""
        logger.debug(f'Creating contact object for AutoTask: {lex_contact}')

        first_name = lex_contact.firstName
        last_name = lex_contact.lastName
        email_address = lex_contact.emailAddress
        phone = lex_contact.phoneNumber

        contact = ContactModel(
            firstName=first_name if first_name else self.default_first_name,
            lastName=last_name if last_name else self.default_last_name,
            emailAddress=email_address,
            phone=phone if phone else self.default_phone,
            isActive=1,
            primaryContact=primary
        )

        return contact

    def assure_company(self: 'AutoTask', lex_company: LexCompany) -> None:
        """Ensure the company exists in AutoTask, creating or updating it as necessary."""
        customer_number = lex_company.roles.get('customer', {}).get('number')
        company_search = self.get(
            f"{self.base_url}/Companies/query?search={
                quote(
                    f'{{"filter": [{{"field": "companyNumber", "op": "eq", "value": "{customer_number}"}}]}}'
                )
            }"
        )
        company_search_object = company_search.json()
        companies = company_search_object.get('items', [])

        if len(companies) == 0:
            logger.info(
                f'Create company (Lex Customer: {lex_company.name}[{customer_number}]) in AutoTask.'
            )

            self.create_company(lex_company)

        if len(companies) == 1:
            company: dict = companies[0]
            logger.info(f'Update company (Lex Customer: {lex_company.name}[{customer_number}]) in AutoTask.')

            autotask_id = company.get('id')
            self.update_company(lex_company, autotask_id)

        if len(companies) > 1:
            logger.error(
                f"Company (Lex Customer: {lex_company.name}[{customer_number}]) exists multiple times in AutoTask."
            )

    def create_company(self: 'AutoTask', lex_company: LexCompany) -> dict:
        """Create a new company in AutoTask."""
        logger.debug(f'Creating company in AutoTask: {lex_company}')

        companies_url = f"{self.base_url}/Companies"

        # Create the company object
        company = self._create_company_object(lex_company)

        # Create the company in AutoTask
        company_call = self.post(companies_url, json=company.as_dict())
        company_call_object = company_call.json()
        company_id = company_call_object.get('itemId')
        logger.debug(f'Company created with ID: {company_id}')

        # Create a contact for the company
        for idx, contact in enumerate(lex_company.contactPersons):
            logger.debug(f'Creating contact: {contact}')

            contact_model = self._create_contact_object(contact, primary=True if idx == 0 else False)

            contact_result = self.post(
                f'{companies_url}/{company_id}/Contacts',
                json=contact_model.as_dict()
            )
            contact_result_object = contact_result.json()
            contact_id = contact_result_object.get('id')
            logger.debug(f'Contact created with ID: {contact_id}')

        logger.debug('Company created successfully.')

    def update_company(self: 'AutoTask', lex_company: LexCompany, autotask_id: str) -> dict:
        """Update an existing company in AutoTask."""
        logger.debug(f'Updating company in AutoTask: {lex_company}')

        companies_url = f"{self.base_url}/Companies"

        # Create the company object
        company = self._create_company_object(lex_company)
        # Set the company ID
        company.id = autotask_id

        # Update the company in AutoTask
        company_call = self.patch(companies_url, json=company.as_dict())
        company_call_object = company_call.json()
        company_call_id = company_call_object.get('itemId')
        logger.debug(f'Company updated with ID: {company_call_id}')

        # Get all contacts for the company
        contacts_url = f'{companies_url}/{autotask_id}/Contacts'
        autotask_contacts: list[dict] = self.get(contacts_url).json().get('items', [])
        logger.debug(f'Contacts for company: {autotask_contacts}')

        # Log the Lexware contacts
        logger.debug(f'Lexware contacts: {lex_company.contactPersons}')

        # Update the contacts
        for idx, lex_contact in enumerate(lex_company.contactPersons):
            logger.debug(f'Updating contact: {lex_contact}')

            contact_model = self._create_contact_object(lex_contact, primary=True if idx == 0 else False)

            # Check if the contact exists and change the first name if necessary
            contact_id = None
            for ac in autotask_contacts:
                lex_first_name = contact_model.firstName
                lex_last_name = contact_model.lastName
                lex_email = contact_model.emailAddress
                autotask_first_name = ac.get('firstName')
                autotask_last_name = ac.get('lastName')
                autotask_email = ac.get('emailAddress')
                autotask_id = ac.get('id')

                if autotask_email == lex_email:
                    lex_first_name_valid = lex_first_name not in self.overwrite_name_list
                    lex_last_name_valid = lex_last_name not in self.overwrite_name_list
                    autotask_first_name_valid = autotask_first_name not in self.overwrite_name_list
                    autotask_last_name_valid = autotask_last_name not in self.overwrite_name_list

                    contact_id = autotask_id

                    # If the AutoTask First Name is valid and the Lex First Name is not valid,
                    # use the AutoTask First Name
                    if autotask_first_name_valid and not lex_first_name_valid:
                        contact_model.firstName = autotask_first_name

                    # If the AutoTask Last Name is valid and the Lex Last Name is not valid,
                    # use the AutoTask Last Name
                    if autotask_last_name_valid and not lex_last_name_valid:
                        contact_model.lastName = autotask_last_name

                    break

            # Update or create the contact
            if contact_id:
                logger.debug(f'Updating contact with ID: {contact_id}')

                contact_model.id = contact_id
                contact_update = self.patch(
                    f'{contacts_url}',
                    json=contact_model.as_dict()
                )
                contact_update_object: dict = contact_update.json()
                contact_update_id = contact_update_object.get('itemId')
                logger.debug(f'Contact updated with ID: {contact_update_id}')

            else:
                contact_create = self.post(
                    contacts_url,
                    json=contact_model.as_dict()
                )
                contact_create_object = contact_create.json()
                contact_create_id = contact_create_object.get('itemId')
                logger.debug(f'Contact created with ID: {contact_create_id}')

        logger.debug('Company updated successfully.')

    def _create_company_object(self: 'AutoTask', lex_company: LexCompany) -> Company:
        """Create a company object for the AutoTask API."""
        logger.debug(f'Creating company object for AutoTask: {lex_company}')

        # Create a new company object
        company = Company(
            companyName=lex_company.name,
            companyNumber=lex_company.roles.get('customer', {}).get('number')
        )

        # Set the company attributes
        company.ownerResourceID = self.owner_resource_id
        company.taxID = lex_company.taxNumber
        company.phone = lex_company.phoneNumbers[0] if len(lex_company.phoneNumbers) >= 1 else self.default_phone
        company.fax = lex_company.faxNumbers[0] if len(lex_company.faxNumbers) >= 1 else None

        # Set the company address
        if len(lex_company.billing_adresses) >= 1:
            address = lex_company.billing_adresses[0]
            company.address1 = address.street
            company.city = address.city
            company.postalCode = address.zip
            company.countryID = self._get_country_id(address.countryCode)

        return company
