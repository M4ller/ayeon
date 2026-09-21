import pytest

from ayeon.memory.serialization import decode_memory_content, encode_memory_content


def test_encode_memory_content_is_deterministic() -> None:
    first = {
        "z": 1,
        "a": {
            "enabled": True,
            "values": [1, 2, None],
        },
    }
    second = {
        "a": {
            "values": [1, 2, None],
            "enabled": True,
        },
        "z": 1,
    }

    assert encode_memory_content(first) == encode_memory_content(second)


def test_encode_memory_content_produces_utf8_bytes() -> None:
    encoded = encode_memory_content(
        {"message": "Ayeon recuerda: canción"}
    )

    assert isinstance(encoded, bytes)
    assert encoded.decode("utf-8") == (
        '{"message":"Ayeon recuerda: canción"}'
    )


def test_encode_memory_content_rejects_unsupported_values() -> None:
    with pytest.raises(
        TypeError,
        match="memory content contains unsupported value",
    ):
        encode_memory_content({"invalid": object()})


def test_encode_memory_content_rejects_non_string_mapping_keys() -> None:
    with pytest.raises(
        TypeError,
        match="memory content mapping keys must be str",
    ):
        encode_memory_content({1: "invalid"})

@pytest.mark.parametrize(
    "value",
    [float("nan"), float("inf"), float("-inf")],
)
def test_encode_memory_content_rejects_non_finite_floats(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="memory content float must be finite",
    ):
        encode_memory_content({"value": value})

def test_memory_content_round_trip() -> None:
    content = {
        "name": "Ayeon",
        "active": True,
        "count": 3,
        "nested": {
            "values": [1, "dos", None],
        },
    }

    encoded = encode_memory_content(content)
    decoded = decode_memory_content(encoded)

    assert decoded == content


def test_decode_memory_content_rejects_non_object_root() -> None:
    with pytest.raises(
        TypeError,
        match="decoded memory content must be a mapping",
    ):
        decode_memory_content(b'["invalid","root"]')


def test_decode_memory_content_rejects_invalid_json() -> None:
    with pytest.raises(
        ValueError,
        match="invalid encoded memory content",
    ):
        decode_memory_content(b'{"broken":')

@pytest.mark.parametrize(
    "encoded",
    [
        b'{"value":NaN}',
        b'{"value":Infinity}',
        b'{"value":-Infinity}',
    ],
)
def test_decode_memory_content_rejects_non_finite_floats(
    encoded: bytes,
) -> None:
    with pytest.raises(
        ValueError,
        match="invalid encoded memory content",
    ):
        decode_memory_content(encoded)
