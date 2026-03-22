# Type Compatibility Matrix

Type support for `emulate()` — nominal logistics document management cases.

| Python type | Fonction testée (`return emulate()`) | `gpt-5.4` | `gpt-4.1` | `gpt-4.1-mini` | `gpt-5-mini` | `qwen3.5:2b` | `qwen3.5:27b` | `qwen3-vl:8b-instruct` | `qwen3-vl:4b-instruct` |
| --- | --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `int` | `count_parcels(shipment_text: str) -> int` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `float` | `extract_weight_kg(shipment_text: str) -> float` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `bool` | `requires_signature(instructions: str) -> bool` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `str` | `extract_tracking_number(email: str) -> str` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `list` | `list_product_refs(delivery_note: str) -> list` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `dict` | `map_pallet_to_quantity(manifest: str) -> dict` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `List[str]` | `extract_sku_list(delivery_note: str) -> List[str]` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Dict[str, int]` | `count_items_per_pallet(manifest: str) -> Dict[str, int]` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Optional[str]` | `extract_po_number(email: str) -> Optional[str]` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Tuple[str, str]` | `extract_carrier_and_tracking(label: str) -> Tuple[str, str]` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Literal["urgent","standard","express"]` | `classify_shipment_priority(instructions: str) -> Literal[...]` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Union[int, str]` | `parse_shipment_id(text: str) -> Union[int, str]` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `dataclass DeliveryNote` | `parse_delivery_note(text: str) -> DeliveryNote` | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| `dataclass ShipmentRecord (nested Address)` | `parse_shipment_record(text: str) -> ShipmentRecord` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| `Pydantic ParcelLabel` | `parse_parcel_label(text: str) -> ParcelLabel` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Pydantic CustomsDeclaration` | `fill_customs_declaration(text: str) -> CustomsDeclaration` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| `list[dict[str, dict[str, str]]]` | `parse_container_manifest(text: str) -> list[dict[str, dict[str, str]]]` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `UserType = list[dict[...]]` | `parse_container_manifest_user_type(text: str) -> UserType` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Summary

- **Models:** `gpt-5.4`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-5-mini`, `qwen3.5:2b`, `qwen3.5:27b`, `qwen3-vl:8b-instruct`, `qwen3-vl:4b-instruct`
- **Types tested:** 18
- 📅 Updated: 2026-03-22 11:17

_Detailed logs: `logs/types_<model>_<TestClass_test_name>.log`_
