from ayeon.contracts.common import MemoryRecordId, new_memory_record_id
from ayeon.memory.durable_evidence import DurableMemoryEvidenceReader


class FakeDurableMemoryEvidenceReader:
    def __init__(self, payload: bytes | None) -> None:
        self._payload = payload
        self.requested_memory_record_id: MemoryRecordId | None = None

    @property
    def name(self) -> str:
        return "fake_durable_memory_evidence_reader"

    def read_payload(
        self,
        memory_record_id: MemoryRecordId,
    ) -> bytes | None:
        self.requested_memory_record_id = memory_record_id
        return self._payload


def test_durable_memory_evidence_reader_is_runtime_checkable() -> None:
    reader = FakeDurableMemoryEvidenceReader(b"evidence")

    assert isinstance(reader, DurableMemoryEvidenceReader)


def test_durable_memory_evidence_reader_preserves_typed_record_identity(
) -> None:
    memory_record_id = new_memory_record_id()
    reader = FakeDurableMemoryEvidenceReader(b"evidence")

    payload = reader.read_payload(memory_record_id)

    assert payload == b"evidence"
    assert reader.requested_memory_record_id == memory_record_id


def test_durable_memory_evidence_reader_can_report_verified_absence() -> None:
    reader = FakeDurableMemoryEvidenceReader(None)

    payload = reader.read_payload(new_memory_record_id())

    assert payload is None