import scpper
import pytest


def test_find_pages():
    assert scpper.Scpper().find_pages(title="scp-173", limit=1)[0] == scpper.api.Page(1956234)


def test_find_users():
    assert scpper.Scpper().find_users(name="gene", limit=1)[0] == scpper.api.User(634139)


def test_find_page_short_exception():
    with pytest.raises(ValueError):
        scpper.Scpper().find_pages(title="0")


def test_find_page_long_exception():
    with pytest.raises(ValueError):
        scpper.Scpper().find_pages(title="0" * 257)


def test_find_user_short_exception():
    with pytest.raises(ValueError):
        scpper.Scpper().find_users(name="0")


def test_find_user_long_exception():
    with pytest.raises(ValueError):
        scpper.Scpper().find_users(name="0" * 257)


def test_tags():
    assert (
        scpper.Scpper()
        .tags(
            method="and",
            tags="+alagadda, +euclid, +hanged-king, +humanoid, +memetic, +mind-affecting, +performance, +scp, -joke",
            limit=1,
        )[0]
        == scpper.api.Page(3222822)
    )


def test_page_not_found_exception():
    with pytest.raises(scpper.api.NotFoundException):
        scpper.Scpper.get_page(0).get("id")


def test_user_not_found_exception():
    with pytest.raises(scpper.api.NotFoundException):
        scpper.Scpper.get_user(0).get("id")


if __name__ == "__main__":
    pytest.main()
