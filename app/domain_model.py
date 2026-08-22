"""Canonical MARSEL service-domain model.

This module defines the business-domain boundary only. It does not write to
RO App and does not claim that RO App currently exposes every field below.
API persistence mappings must be verified separately against the official
RO App contract before implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ServiceDomain(StrEnum):
    JEWELRY = "JEWELRY"
    WATCH = "WATCH"
    EYEWEAR = "EYEWEAR"


COMMON_OBJECT_FIELDS = frozenset(
    {
        "id",
        "order_id",
        "domain",
        "description",
        "condition_at_intake",
        "completeness",
        "photos",
        "serial_or_external_identifier",
    }
)

DOMAIN_FIELDS: dict[ServiceDomain, frozenset[str]] = {
    ServiceDomain.JEWELRY: frozenset(
        {"metal", "fineness", "mass", "stones", "size", "construction"}
    ),
    ServiceDomain.WATCH: frozenset(
        {"brand", "model", "movement", "serial_number", "case", "crystal", "bracelet_or_strap"}
    ),
    ServiceDomain.EYEWEAR: frozenset(
        {"brand", "model", "frame_type", "frame_material", "color", "lens_type", "lens_condition", "nose_pads", "temples", "fasteners"}
    ),
}


@dataclass(frozen=True, slots=True)
class ServiceObject:
    id: str
    order_id: str
    domain: ServiceDomain
    description: str = ""
    condition_at_intake: str = ""
    completeness: tuple[str, ...] = ()
    photos: tuple[str, ...] = ()
    serial_or_external_identifier: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        allowed = DOMAIN_FIELDS[self.domain]
        invalid = set(self.attributes) - allowed
        if invalid:
            raise ValueError(
                f"attributes {sorted(invalid)} are not valid for domain {self.domain}"
            )


@dataclass(frozen=True, slots=True)
class ServiceOrder:
    id: str
    customer_id: str
    objects: tuple[ServiceObject, ...] = ()
    status: str = "RECEIVED"
    currency: str = "RUB"

    def validate(self) -> None:
        if not self.id:
            raise ValueError("order id is required")
        if not self.customer_id:
            raise ValueError("customer_id is required")
        if self.currency != "RUB":
            raise ValueError("MARSEL canonical currency is RUB")
        for obj in self.objects:
            if obj.order_id != self.id:
                raise ValueError("service object order_id must match order id")
            obj.validate()
