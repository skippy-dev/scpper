###############################################################################
# Module Imports
###############################################################################

import scpper.utils

from typing import Callable, List, Any
import json

try:
    from functools import cached_property
except ImportError:
    from functools import lru_cache

    def cached_property(func: Callable[[None], Any]) -> property:
        return property(lru_cache(func))


###############################################################################
# API Classes
###############################################################################


class BaseScpperItemClass:

    """Base class for Scpper item

    Attributes:
        id: Wikidot id of the item to retrieve.
    """

    _endpoint: str

    ###########################################################################
    # Special Methods
    ###########################################################################

    def __init__(self, _id: int):
        self.id = _id
        self.req = scpper.utils.InsistentRequest()

    def __repr__(self):
        return "{}.{}({})".format(
            self.__module__, self.__class__.__name__, repr(self.id)
        )

    def __getattr__(self, name: str) -> Any:
        return self._data[name]

    __getitem__ = __getattr__

    ###########################################################################
    # Properties
    ###########################################################################

    @cached_property
    def _data(self):
        """Retrieves a item data by id.

        Returns:
            A dict object containing a item metadata.

        Raises:
            scpper.utils.NotFoundException: Item not found.
        """
        res = self.req.get(self._endpoint, params={"id": self.id})
        data = json.loads(res.text)
        if "error" in data:
            raise scpper.utils.NotFoundException(data["error"])

        return data


class Page(BaseScpperItemClass):

    """Scpper page class

    Attributes:
        id: Wikidot id of the page to retrieve.
    """

    _endpoint = "http://scpper.com/api/page"


class User(BaseScpperItemClass):

    """Scpper user class"""

    _endpoint = "http://scpper.com/api/user"


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

    ###########################################################################
    # Special Methods
    ###########################################################################

    def __init__(self, site: str = "en"):
        self.site = site
        self.req = scpper.utils.InsistentRequest()

    def __repr__(self) -> str:
        return "{}.{}({})".format(
            self.__module__, self.__class__.__name__, repr(self.site)
        )

    ###########################################################################
    # Public Methods
    ###########################################################################

    def find_pages(self, title: str, limit: int = 50, random: int = 0) -> List[Page]:

        """Retrieves up to limit pages from the specified wiki with part of the name matching title.

        Args:
            title:
                Search query, part of page's name (i.e. "173" will match "SCP-173", "SCP-1173", etc). Between 3 and 256 characters.
            limit:
                Maximum number of rows returned by the query. Limited to 50.
            random:
                Bit flag indicating whether resulting list of pages should be randomized.
                "0" - returns limit pages ordered by (kind of) relevance, descending (default)
                "1" - returns random selection of limit pages from the original query.

        Returns:
            A list object containing all found pages.

        Raises:
            ValueError: Title must be between 3 and 256 characters long.
        """

        if len(title) < 3 or len(title) > 256:
            raise ValueError("Title must be between 3 and 256 characters long")

        res = self.req.get(
            "http://scpper.com/api/find-pages",
            params={
                "site": self.site,
                "title": title,
                "limit": limit,
                "random": random,
            },
        )
        pages = json.loads(res.text)["pages"]

        return [Page(page["id"]) for page in pages]

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

        res = self.req.get(
            "http://scpper.com/api/find-users",
            params={"site": self.site, "name": name, "limit": limit},
        )
        users = json.loads(res.text)["users"]

        return [User(user["id"]) for user in users]

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

        res = self.req.get(
            "http://scpper.com/api/tags",
            params={
                "site": self.site,
                "method": method,
                "tags": tags,
                "limit": limit,
                "random": random,
            },
        )
        pages = json.loads(res.text)["pages"]

        return [Page(page["id"]) for page in pages]
