"""This module contains classes for handling AutoTask requests and representing companies."""

from dataclasses import asdict, dataclass, field
from typing import Dict, List
from urllib.parse import quote

import requests

from autolex.classes.lexware import Company as LexCompany


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
        owner_resource_id: int
    ) -> None:
        """Initialize the AutoTask class."""
        super().__init__()
        self.base_url = base_url
        self.api_user = api_user
        self.api_key = api_key
        self.api_integration_code = api_integration_code
        self.owner_resource_id = owner_resource_id
        self.headers = {
            'ApiIntegrationCode': self.api_integration_code,
            'UserName': self.api_user,
            'Secret': self.api_key,
        }

    def _get_country_id(self: 'AutoTask', country_code: str) -> int:
        """Get the country ID for a given country code."""
        quoted_search = quote(f'{{"filter": [{{"field": "countryCode", "op": "eq", "value": "{country_code}"}}]}}')
        countries_url = f"{self.base_url}/Countries/query?search={quoted_search}"
        countries = self.get(countries_url).json()

        for country in countries.get('items', []):
            if country.get('countryCode') == country_code:
                return country.get('id')

    def create_company(self: 'AutoTask', lex_company: LexCompany) -> dict:
        """Create a new company in AutoTask."""
        companies_url = f"{self.base_url}/Companies"

        # Create a new company object
        company = Company(
            companyName=lex_company.name,
            companyNumber=lex_company.roles.get('customer', {}).get('number')
        )

        # Set the company attributes
        company.ownerResourceID = self.owner_resource_id
        company.taxID = lex_company.taxNumber
        company.phone = lex_company.phoneNumbers[0] if len(lex_company.phoneNumbers) >= 1 else None
        company.fax = lex_company.faxNumbers[0] if len(lex_company.faxNumbers) >= 1 else None
        # company.webAddress = lex_company.web  # TODO: Web address is not in Lexware

        # Set the company address
        if len(lex_company.shipping_adresses) >= 1:
            address = lex_company.shipping_adresses[0]
            company.address1 = address.street
            company.city = address.city
            company.postalCode = address.zip
            company.countryID = self._get_country_id(address.countryCode)

        if len(lex_company.billing_adresses) >= 1:
            address = lex_company.billing_adresses[0]
            company.billingAddress1 = address.street
            company.billToCity = address.city
            company.billToZipCode = address.zip
            company.billToCountryID = self._get_country_id(address.countryCode)

        # Create the company in AutoTask
        company_call = self.post(companies_url, json=company.as_dict())
        company_call_object = company_call.json()
        company_id = company_call_object.get('itemId')

        # Create a contact for the company
        for contact in lex_company.contactPersons:
            contact_model = ContactModel(
                firstName=contact.firstName,
                lastName=contact.lastName,
                emailAddress=contact.emailAddress,
                phone=contact.phoneNumber,
                isActive=1,
                primaryContact=True
            )

            self.post(
                f'{companies_url}/{company_id}/Contacts',
                json=contact_model.as_dict()
            ) # TODO Check what happens with multiple users
