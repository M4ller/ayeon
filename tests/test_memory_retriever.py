from ayeon.contracts.common import MemoryRecordId
from ayeon.contracts.memory_retrieval import MemoryRetrievalResult
from ayeon.memory.retriever import MemoryRetriever


class CompatibleMemoryRetriever:
    @property
    def name(self) -> str:
        return "compatible_memory_retriever"

    def retrieve(
        self,
        memory_record_id: MemoryRecordId,
    ) -> MemoryRetrievalResult:
        raise NotImplementedError


class IncompatibleMemoryRetriever:
    pass


def test_compatible_memory_retriever_satisfies_protocol() -> None:
    assert isinstance(CompatibleMemoryRetriever(), MemoryRetriever)


def test_incompatible_memory_retriever_does_not_satisfy_protocol() -> None:
    assert not isinstance(IncompatibleMemoryRetriever(), MemoryRetriever)