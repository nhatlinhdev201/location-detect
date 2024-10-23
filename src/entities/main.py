from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    id: int
    address: str
    city_id: int
    city_name: str
    district_id: int
    district_name: str
    ward_id: int
    ward_name: str
    street_name: str
    type_address: str

class ListAddress(BaseModel):
    addresses: List[Address]

class AddressRequest(BaseModel):
    locations: List[str]


class SearchRequest(BaseModel):
    input: str
