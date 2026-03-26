"""
tests/typing/test_compat_logistics.py
--------------------------------------
Type compatibility battery — nominal cases only.
Domain: document management in logistics (shipments, waybills, delivery notes,
customs declarations).

One test = one Python type. Tests are designed to be straightforward and
representative, NOT to probe edge cases.

COMPAT_META (list of tuples) drives the markdown report:
    (pytest_test_id, python_type_display, function_signature_display)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Union, Literal

import pytest
from pydantic import BaseModel

from OpenHosta import emulate


# ── Domain dataclasses ────────────────────────────────────────────────────────

@dataclass
class Address:
    street: str
    city: str
    zip_code: str
    country: str


@dataclass
class ShipmentRecord:
    tracking_number: str
    carrier: str
    origin: Address
    destination: Address
    weight_kg: float
    n_parcels: int


@dataclass
class DeliveryNote:
    reference: str
    supplier: str
    recipient: str
    items: List[str]
    total_pieces: int


# ── Domain Pydantic models ────────────────────────────────────────────────────

class ParcelLabel(BaseModel):
    tracking_number: str
    carrier: str
    weight_kg: float
    priority: str


class CustomsDeclaration(BaseModel):
    exporter: str
    importer: str
    hs_code: str
    description: str
    declared_value_eur: float
    country_of_origin: str


# ── Business fixtures ─────────────────────────────────────────────────────────

SHIPMENT_TEXT = (
    "Shipping order #BOL-2024-10892 from Rungis Logistics Hub "
    "(12 rue du Commerce, 94550 Rungis, France) to Rhine Warehouse GmbH "
    "(Industriestrasse 45, 68199 Mannheim, Germany). "
    "Carrier: DHL Freight. 3 pallets, total weight 487.5 kg."
)

DELIVERY_NOTE_TEXT = (
    "Bon de livraison BL-2024-55301. Fournisseur: Plastiques du Nord SARL. "
    "Destinataire: Atelier Mécanique Renard. "
    "Contenu: boîtes de joints toriques (ref. JT-08), rouleaux de film "
    "rétractable (ref. FR-120), palettes Europe (ref. EPAL-1). Total: 240 pièces."
)

EMAIL_WITH_PO = (
    "Bonjour, suite à votre commande PO-2024-78123, nous confirmons l'expédition "
    "de ce jour. Le numéro de suivi DHL est 1Z999AA10123456784. Cordialement."
)

EMAIL_NO_PO = (
    "Bonjour, nous accusons réception de votre colis et procédons à l'inspection."
)

PARCEL_LABEL_TEXT = (
    "DHL EXPRESS WORLDWIDE\n"
    "Tracking: 1Z999AA10123456784\n"
    "Weight: 12.3 kg\n"
    "Priority: EXPRESS"
)

MANIFEST_TEXT = (
    "Manifest #MAN-2024-001. "
    "Pallet P1: 48 cartons ref SKU-001. "
    "Pallet P2: 36 cartons ref SKU-002. "
    "Pallet P3: 60 cartons ref SKU-003."
)

CUSTOMS_TEXT = (
    "Export declaration. Exporter: Électronique Ouest SAS, Nantes, France. "
    "Importer: TechDistrib GmbH, Frankfurt, Germany. "
    "Goods: Industrial electronic control modules. HS code: 8537.10. "
    "Country of origin: France. Declared value: EUR 28 400."
)

URGENT_INSTRUCTIONS = "URGENT — livraison avant 8h le lendemain, signature obligatoire."

MIXED_ID_TEXT  = "L'expédition référencée SHIP-2024-XK9921 est prête pour enlèvement."

CONTAINER_MANIFEST_TEXT = (
    "Shipment includes 2 containers. "
    "Container CONT-100: SKU-A - 'Widgets', SKU-B - 'Gadgets'. "
    "Container CONT-200: SKU-C - 'Gizmos'."
)


# ── Tests ─────────────────────────────────────────────────────────────────────

UserType = list[dict[str, dict[str, str]]]

class Item(BaseModel):
    name: str
    quantity: int

class Order(BaseModel):
    items: List[Item]
    customer: str

class TestCompatLogistics:

    def test_int(self):
        def count_parcels(shipment_text: str) -> int:
            """Return the total number of parcels described in the shipment text."""
            return emulate()
        result = count_parcels(SHIPMENT_TEXT)
        assert isinstance(result, int)
        assert result > 0

    def test_float(self):
        def extract_weight_kg(shipment_text: str) -> float:
            """Extract the total weight in kilograms from the shipment description."""
            return emulate()
        result = extract_weight_kg(SHIPMENT_TEXT)
        assert isinstance(result, float)
        assert result > 0.0

    def test_bool(self):
        def requires_signature(instructions: str) -> bool:
            """Return True if the delivery instructions require a recipient signature."""
            return emulate()
        result = requires_signature(URGENT_INSTRUCTIONS)
        assert isinstance(result, bool)
        assert result is True

    def test_str(self):
        def extract_tracking_number(email: str) -> str:
            """Extract the carrier tracking number from the email body."""
            return emulate()
        result = extract_tracking_number(EMAIL_WITH_PO)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_list(self):
        def list_product_refs(delivery_note: str) -> list:
            """Return a list of product/SKU references found in the delivery note."""
            return emulate()
        result = list_product_refs(DELIVERY_NOTE_TEXT)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_dict(self):
        def map_pallet_to_quantity(manifest: str) -> dict:
            """Return a dict mapping each pallet ID to its carton count."""
            return emulate()
        result = map_pallet_to_quantity(MANIFEST_TEXT)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_List_str(self):
        def extract_sku_list(delivery_note: str) -> List[str]:
            """Return the list of SKU/product reference codes in the delivery note."""
            return emulate()
        result = extract_sku_list(DELIVERY_NOTE_TEXT)
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)

    def test_Dict_str_int(self):
        def count_items_per_pallet(manifest: str) -> Dict[str, int]:
            """Return a mapping of pallet reference to its item count."""
            return emulate()
        result = count_items_per_pallet(MANIFEST_TEXT)
        assert isinstance(result, dict)
        assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())

    def test_Optional_str(self):
        def extract_po_number(email: str) -> Optional[str]:
            """
            Extract the purchase order number from the email if one is present.
            Return None if no PO number can be found.
            """
            return emulate()
        # Case present
        result_present = extract_po_number(EMAIL_WITH_PO)
        assert result_present is not None and isinstance(result_present, str)
        # Case absent
        result_absent = extract_po_number(EMAIL_NO_PO)
        assert result_absent is None

    def test_Tuple_str_str(self):
        def extract_carrier_and_tracking(label: str) -> Tuple[str, str]:
            """Return a tuple (carrier_name, tracking_number) from the parcel label."""
            return emulate()
        result = extract_carrier_and_tracking(PARCEL_LABEL_TEXT)
        assert isinstance(result, tuple) and len(result) == 2
        assert all(isinstance(s, str) for s in result)

    def test_Literal(self):
        def classify_shipment_priority(instructions: str) -> Literal["urgent", "standard", "express"]:
            """Classify the shipment priority as 'urgent', 'standard', or 'express'."""
            return emulate()
        result = classify_shipment_priority(URGENT_INSTRUCTIONS)
        assert result in ("urgent", "standard", "express")

    def test_Union_int_str(self):
        def parse_shipment_id(text: str) -> Union[int, str]:
            """
            Extract the shipment identifier from the text.
            Return it as int if it is purely numeric, as str otherwise.
            """
            return emulate()
        result = parse_shipment_id(MIXED_ID_TEXT)
        assert isinstance(result, (int, str))

    def test_dataclass_flat(self):
        def parse_delivery_note(text: str) -> DeliveryNote:
            """Extract all delivery note fields from the document text."""
            return emulate()
        result = parse_delivery_note(DELIVERY_NOTE_TEXT)
        assert isinstance(result, DeliveryNote)
        assert isinstance(result.reference, str)
        assert isinstance(result.items, list)
        assert isinstance(result.total_pieces, int)

    def test_dataclass_nested(self):
        def parse_shipment_record(text: str) -> ShipmentRecord:
            """
            Extract the complete shipment record, including nested
            origin and destination Address objects.
            """
            return emulate()
        result = parse_shipment_record(SHIPMENT_TEXT)
        assert isinstance(result, ShipmentRecord)
        assert isinstance(result.origin, Address)
        assert isinstance(result.destination, Address)
        assert isinstance(result.weight_kg, float)

    def test_pydantic_nested(self):
        def parse_order(text: str) -> Order:
            """Extract the order details including the list of items."""
            return emulate()
        
        ORDER_TEXT = "Order for John Doe: 2x Widgets, 1x Gadget."
        result = parse_order(ORDER_TEXT)
        assert isinstance(result, Order)
        assert isinstance(result.items, list)
        assert len(result.items) == 2
        assert isinstance(result.items[0], Item)
        assert result.items[0].name == "Widgets"
        assert result.items[1].name == "Gadget"

    def test_pydantic_flat(self):
        def parse_parcel_label(text: str) -> ParcelLabel:
            """Parse the raw parcel label text into a structured ParcelLabel."""
            return emulate()
        result = parse_parcel_label(PARCEL_LABEL_TEXT)
        assert isinstance(result, ParcelLabel)
        assert isinstance(result.tracking_number, str)
        assert isinstance(result.weight_kg, float)

    def test_pydantic_with_optional(self):
        def fill_customs_declaration(text: str) -> CustomsDeclaration:
            """Extract all customs declaration fields from the document text."""
            return emulate()
        result = fill_customs_declaration(CUSTOMS_TEXT)
        assert isinstance(result, CustomsDeclaration)
        assert isinstance(result.declared_value_eur, float)
        assert isinstance(result.hs_code, str)

    def test_complex_list_dict(self):
        def parse_container_manifest(text: str) -> list[dict[str, dict[str, str]]]:
            """
            Extract a list of containers. Each container is a dictionary mapping the container ID
            to another dictionary of SKU codes and their descriptions.
            """
            return emulate()
        result = parse_container_manifest(CONTAINER_MANIFEST_TEXT)
        assert isinstance(result, list)
        if len(result) > 0:
            assert isinstance(result[0], dict)

    def test_user_type_alias(self):
        def parse_container_manifest_user_type(text: str) -> UserType:
            """
            Extract a list of containers. Each container is a dictionary mapping the container ID
            to another dictionary of SKU codes and their descriptions.
            """
            return emulate()
        result = parse_container_manifest_user_type(CONTAINER_MANIFEST_TEXT)
        assert isinstance(result, list)
        if len(result) > 0:
            assert isinstance(result[0], dict)


# ── Report metadata ───────────────────────────────────────────────────────────
# List of (pytest_test_id, python_type_display, function_signature)
# Consumed by the bash report generator (Phase 3).

COMPAT_META = [
    (
        "TestCompatLogistics::test_int",
        "int",
        "count_parcels(shipment_text: str) -> int",
    ),
    (
        "TestCompatLogistics::test_float",
        "float",
        "extract_weight_kg(shipment_text: str) -> float",
    ),
    (
        "TestCompatLogistics::test_bool",
        "bool",
        "requires_signature(instructions: str) -> bool",
    ),
    (
        "TestCompatLogistics::test_str",
        "str",
        "extract_tracking_number(email: str) -> str",
    ),
    (
        "TestCompatLogistics::test_list",
        "list",
        "list_product_refs(delivery_note: str) -> list",
    ),
    (
        "TestCompatLogistics::test_dict",
        "dict",
        "map_pallet_to_quantity(manifest: str) -> dict",
    ),
    (
        "TestCompatLogistics::test_List_str",
        "List[str]",
        "extract_sku_list(delivery_note: str) -> List[str]",
    ),
    (
        "TestCompatLogistics::test_Dict_str_int",
        "Dict[str, int]",
        "count_items_per_pallet(manifest: str) -> Dict[str, int]",
    ),
    (
        "TestCompatLogistics::test_Optional_str",
        "Optional[str]",
        "extract_po_number(email: str) -> Optional[str]",
    ),
    (
        "TestCompatLogistics::test_Tuple_str_str",
        "Tuple[str, str]",
        "extract_carrier_and_tracking(label: str) -> Tuple[str, str]",
    ),
    (
        "TestCompatLogistics::test_Literal",
        'Literal["urgent","standard","express"]',
        'classify_shipment_priority(instructions: str) -> Literal[...]',
    ),
    (
        "TestCompatLogistics::test_Union_int_str",
        "Union[int, str]",
        "parse_shipment_id(text: str) -> Union[int, str]",
    ),
    (
        "TestCompatLogistics::test_dataclass_flat",
        "dataclass DeliveryNote",
        "parse_delivery_note(text: str) -> DeliveryNote",
    ),
    (
        "TestCompatLogistics::test_dataclass_nested",
        "dataclass ShipmentRecord (nested Address)",
        "parse_shipment_record(text: str) -> ShipmentRecord",
    ),
    (
        "TestCompatLogistics::test_pydantic_flat",
        "Pydantic ParcelLabel",
        "parse_parcel_label(text: str) -> ParcelLabel",
    ),
    (
        "TestCompatLogistics::test_pydantic_with_optional",
        "Pydantic CustomsDeclaration",
        "fill_customs_declaration(text: str) -> CustomsDeclaration",
    ),
    (
        "TestCompatLogistics::test_complex_list_dict",
        "list[dict[str, dict[str, str]]]",
        "parse_container_manifest(text: str) -> list[dict[str, dict[str, str]]]",
    ),
    (
        "TestCompatLogistics::test_user_type_alias",
        "UserType = list[dict[...]]",
        "parse_container_manifest_user_type(text: str) -> UserType",
    ),
]
