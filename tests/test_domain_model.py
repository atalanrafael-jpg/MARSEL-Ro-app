from app.domain_model import DOMAIN_FIELDS, ServiceDomain, ServiceObject, ServiceOrder


def test_all_three_service_domains_are_canonical() -> None:
    assert set(ServiceDomain) == {
        ServiceDomain.JEWELRY,
        ServiceDomain.WATCH,
        ServiceDomain.EYEWEAR,
    }


def test_eyewear_has_its_own_specialized_fields() -> None:
    assert "frame_type" in DOMAIN_FIELDS[ServiceDomain.EYEWEAR]
    assert "movement" not in DOMAIN_FIELDS[ServiceDomain.EYEWEAR]
    assert "fineness" not in DOMAIN_FIELDS[ServiceDomain.EYEWEAR]


def test_domain_fields_cannot_cross_contaminate() -> None:
    obj = ServiceObject(
        id="obj-1",
        order_id="order-1",
        domain=ServiceDomain.EYEWEAR,
        attributes={"movement": "automatic"},
    )
    try:
        obj.validate()
    except ValueError as exc:
        assert "movement" in str(exc)
    else:
        raise AssertionError("cross-domain field was accepted")


def test_order_requires_rub_and_matching_object_order() -> None:
    order = ServiceOrder(
        id="order-1",
        customer_id="customer-1",
        currency="RUB",
        objects=(
            ServiceObject(
                id="obj-1",
                order_id="order-1",
                domain=ServiceDomain.EYEWEAR,
                attributes={"frame_type": "full-rim"},
            ),
        ),
    )
    order.validate()
