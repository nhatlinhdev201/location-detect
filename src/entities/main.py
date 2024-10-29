from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    address_id: int
    address: str
    city_id: int
    city_name: str
    district_id: int
    district_name: str
    ward_id: int
    ward_name: str
    street_name: str
    lat: str
    lng: str

class Address_3(BaseModel):
    city_id: int
    city_name: str
    district_id: int
    district_name: str
    ward_id: int
    ward_name: str

class Address_level(BaseModel):
    id: int
    name: str
    code_local: str
    type: int
    parent_id: int

class ListAddress(BaseModel):
    addresses: List[Address]

class AddressRequest(BaseModel):
    locations: List[str]


class SearchRequest(BaseModel):
    input: str
