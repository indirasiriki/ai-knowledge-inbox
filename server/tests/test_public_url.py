import pytest

from app.errors import HttpError
from app.services.public_url import assert_public_url


@pytest.mark.parametrize("value", [
    "http://127.0.0.1/a",
    "http://10.1.2.3/a",
    "http://192.168.0.8/a",
    "http://172.16.5.5/a",
    "http://169.254.169.254/latest",
    "http://0.0.0.0/",
    "http://localhost/a",
    "http://[::1]/a",
    "http://[fc00::1]/a",
    "ftp://example.com/a",
    "http://user:pass@1.1.1.1/a",
    "not a url",
])
def test_rejects_hosts_that_are_not_public(value):
    with pytest.raises(HttpError) as caught:
        assert_public_url(value)
    assert caught.value.status == 400


def test_accepts_a_public_address_literal():
    parsed = assert_public_url("https://1.1.1.1/docs")
    assert parsed.geturl() == "https://1.1.1.1/docs"
