from typing import List, Any
import requests

try:
    from functools import cached_property
except ImportError:
    from functools import lru_cache

    cached_property = lambda func: property(lru_cache()(func))


class BaseScpperObject:

    """Base class for Scpper item

    Attributes:
        id: Wikidot id of the item to retrieve.
    """

    _endpoint: str

    def __init__(self, _id: int):
        self.id = _id

    def __repr__(self) -> str:
        return f"{self.__module__}.{self.__class__.__name__}({self.id})"

    def __eq__(self, other: Any) -> bool:
        if not hasattr(other, "_endpoint") or not hasattr(other, "id"):
            return False
        return self._endpoint == other._endpoint and self.id == other.id

    def get(self, name: str) -> Any:
        return self._data[name]

    @cached_property
    def _data(self) -> Any:
        """Retrieves an item data by id.

        Returns:
            A dict object containing an item metadata.

        Raises:
            scpper.utils.NotFoundException: Item not found.
        """
        data = requests.get(self._endpoint, params={"id": self.id}).json()
        if "error" in data:
            raise NotFoundException(data["error"])

        return data

    __getitem__ = __getattr__ = get


class Page(BaseScpperObject):

    """Scpper page class"""

    _endpoint = "https://scpper.com/api/page"


class User(BaseScpperObject):

    """Scpper user class"""

    _endpoint = "https://scpper.com/api/user"


class Scpper:

    """Scpper API wrapper class

    Attributes:
        site: Branch site name.
            SCP Foundation (scp-wiki.net): "en"
            Russian branch (scpfoundation.ru): "ru"
            Korean branch (ko.scp-wiki.net): "ko"
            Japanese branch (ja.scp-wiki.net): "ja"
            French branch (fondationscp.wikidot.com): "fr"
            Spanish branch (lafundacionscp.wikidot.com): "es"
            Thai branch (scp-th.wikidot.com): "th"
            Polish branch (scp-wiki.net.pl): "pl"
            German branch (scp-wiki-de.wikidot.com): "de"
            Chinese branch (scp-wiki-cn.wikidot.com): "cn"
            Italian branch (fondazionescp.wikidot.com): "it"
            SCP International (scp-int.wikidot.com): "int"
    """

    def __init__(self, site: str = "en"):
        self.site = site

    def __repr__(self) -> str:
        return "{}.{}({})".format(
            self.__module__, self.__class__.__name__, repr(self.site)
        )

    @staticmethod
    def get_page(_id: int) -> Page:
        return Page(_id)

    @staticmethod
    def get_user(_id: int) -> User:
        return User(_id)

    def find_pages(self, title: str, limit: int = 50, random: bool = False) -> List[Page]:

        """Retrieves up to limit pages from the specified wiki with part of the name matching title.

        Args:
            title:
                Search query, part of page's name (i.e. "173" will match "SCP-173", "SCP-1173", etc). Between 3 and 256 characters.
            limit:
                Maximum number of rows returned by the query. Limited to 50.
            random:
                Bool indicating whether resulting list of pages should be randomized.
                False - returns limit pages ordered by (kind of) relevance, descending (default)
                True - returns random selection of limit pages from the original query.

        Returns:
            A list object containing all found pages.

        Raises:
            ValueError: Title must be between 3 and 256 characters long.
        """

        if len(title) < 3 or len(title) > 256:
            raise ValueError("Title must be between 3 and 256 characters long")

        pages = requests.get(
            "https://scpper.com/api/find-pages",
            params={
                "site": self.site,
                "title": title,
                "limit": limit,
                "random": int(random),
            },
        ).json()["pages"]

        return [self.get_page(page["id"]) for page in pages]

    def find_users(self, name: str, limit: int = 50) -> List[User]:

        """Retrieves up to limit users from the with part of the name matching name.

        Args:
            name:
                Search query, part of user's name (i.e. "cle" will match "Dr Clef", "Agent MacLeod", etc). Between 3 and 256 characters.
            limit:
                Maximum number of rows returned by the query. Limited to 50.

        Returns:
            A list object containing all found users.

        Raises:
            ValueError: Name must be between 3 and 256 characters long.
        """

        if len(name) < 3 or len(name) > 256:
            raise ValueError("Name must be between 3 and 256 characters long")

        users = requests.get(
            "https://scpper.com/api/find-users",
            params={
                "site": self.site,
                "name": name,
                "limit": limit},
        ).json()["users"]

        return [self.get_user(user["id"]) for user in users]

    def tags(
        self, tags: str, method: str = "and", limit: int = 50, random: int = 0
    ) -> List[Page]:

        """Retrieves up to limit pages from the specified wiki, selected using provided tags.

        Args:
            method:
                How to combine provided tags for the query ("and"/"or")
                "and" - only pages that have all the tags (default)
                "or" - pages that contain any of the tags.
            tags:
                List of tags, each prefixed with "+" or "-", separated by commas
                "+" indicates that pages containing this tag must be included in the query
                "-" indicates that pages containing this tag must be excluded from the query
                Each tag MUST be prefixed by only ONE of those options.
            limit:
                Maximum number of rows returned by the query. Limited to 50.
            random:
                Bit flag indicating whether resulting list of pages should be randomized.
                "0" - returns limit pages ordered by clean rating, descending (default)
                "1" - returns random selection of limit pages from the original query.

        Returns:
            A list object containing all selected pages.
        """

        pages = requests.get(
            "https://scpper.com/api/tags",
            params={
                "site": self.site,
                "method": method,
                "tags": tags,
                "limit": limit,
                "random": random,
            },
        ).json()["pages"]

        return [self.get_page(page["id"]) for page in pages]


class NotFoundException(Exception):
    pass

