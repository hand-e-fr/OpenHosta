import pytest

from OpenHosta import emulate

from typing import Optional

from pydantic import BaseModel

class Town(BaseModel):
    country: str
    long: float
    lat: float


class Client(BaseModel):
    name: str
    surname: str
    company: str
    email: str
    town: str
    address: str


class Address(BaseModel):
    street: str
    city: str


class Person(BaseModel):
    name: str
    address: Address

class GuardedTown(BaseModel):
    country: str
    long: float
    lat: float


class MaybeTown(BaseModel):
    country: str
    long: float
    lat: float
    zipcode: Optional[int] = None


class TestEmulatePydanticclasses:
    def test_emulate_returns_basic_dataclass(self):
        def find_town(town_name: str) -> Town:
            """
            Return the country and GPS coordinates of the town in parameter.
            """
            return emulate()

        result = find_town("Glasgow")

        assert isinstance(result, Town)
        assert isinstance(result.country, str)
        assert isinstance(result.long, float)
        assert isinstance(result.lat, float)

    def test_emulate_extracts_client_dataclass(self):
        def extract_client_name(text: str) -> Client:
            """
            Extract client information from the email text.
            """
            return emulate()

        result = extract_client_name(
            "FROM: sebastien@somecorp.com\n"
            "TO: shipment@hand-e.fr\n"
            "Object: do not send mail support@somecorp.com\n\n"
            "Hello Bob, I am Sebastian from Paris, France. "
            "Could you send me a sample of your main product? "
            "My office address is 3 rue de la république, Lyon 1er."
        )

        assert isinstance(result, Client)
        assert isinstance(result.name, str)
        assert isinstance(result.surname, str)
        assert isinstance(result.company, str)
        assert isinstance(result.email, str)
        assert isinstance(result.town, str)
        assert isinstance(result.address, str)
        assert result.email

    def test_emulate_returns_guarded_dataclass(self):
        def find_town(town_name: str) -> GuardedTown:
            """
            Return the country and GPS coordinates of the town in parameter.
            """
            return emulate()

        result = find_town("Glasgow")

        assert isinstance(result, GuardedTown)
        assert isinstance(result.country, str)
        assert isinstance(result.long, float)
        assert isinstance(result.lat, float)

    def test_emulate_returns_nested_dataclass(self):
        def extract_person(text: str) -> Person:
            """
            Extract a person name and address from the text.
            """
            return emulate()

        result = extract_person(
            "John lives at 12 Baker Street in London."
        )

        assert isinstance(result, Person)
        assert isinstance(result.name, str)
        assert isinstance(result.address, Address)
        assert isinstance(result.address.street, str)
        assert isinstance(result.address.city, str)

    def test_emulate_returns_dataclass_with_optional_field(self):
        def find_town_with_zipcode(town_name: str) -> MaybeTown:
            """
            Return the country and GPS coordinates of the town.
            Include zipcode if known, otherwise leave it null.
            """
            return emulate()

        result = find_town_with_zipcode("Glasgow")

        assert isinstance(result, MaybeTown)
        assert isinstance(result.country, str)
        assert isinstance(result.long, float)
        assert isinstance(result.lat, float)
        assert result.zipcode is None or isinstance(result.zipcode, int)