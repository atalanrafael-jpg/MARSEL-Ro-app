from app.integrations.adapter import (
    ProductionWriteBlocked,
    assert_write_gate,
    deterministic_idempotency_key,
    retry_with_backoff,
)


def test_idempotency_key_is_deterministic():
    a = deterministic_idempotency_key(provider="website", entity="order", external_id="42", operation="UPDATE")
    b = deterministic_idempotency_key(provider="website", entity="order", external_id="42", operation="UPDATE")
    assert a == b


def test_write_requires_both_gates():
    try:
        assert_write_gate(provider_gate=True, production_gate=False)
    except ProductionWriteBlocked:
        pass
    else:
        raise AssertionError("production WRITE must remain blocked")


def test_retry_retries_declared_transient_errors():
    calls = []

    def operation():
        calls.append(1)
        if len(calls) < 2:
            raise TimeoutError("transient")
        return "ok"

    assert retry_with_backoff(operation, attempts=2, base_delay=0) == "ok"
    assert len(calls) == 2
