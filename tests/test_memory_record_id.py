from ayeon.contracts.common import (
    MemoryRecordId,
    new_memory_record_id,
)


def test_memory_record_ids_are_unique() -> None:
    first = new_memory_record_id()
    second = new_memory_record_id()

    assert first != second


def test_memory_record_id_factory_returns_memory_record_id() -> None:
    memory_record_id = new_memory_record_id()

    assert isinstance(memory_record_id, MemoryRecordId.__supertype__)
