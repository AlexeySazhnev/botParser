import json
import re
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from bs4 import BeautifulSoup # type: ignore

from src.common.async_provider.aiohttp import AiohttpProvider
from src.common.async_provider.base import AsyncProvider
from src.common.async_provider.types import RequestMethodType

ResponseType = TypeVar("ResponseType")
IterResult = TypeVar("IterResult")


def _make_variables(
    *,
    sort: str = "DEFAULT",
    attributes: List[Dict[str, Any]],
    data_published: Optional[Any] = None,
    location: Dict[str, Any],
    search: str = "",
    cursor: str = "",
) -> Dict[str, Any]:
    return {
        "sort": sort,
        "attributes": attributes,
        "datePublished": data_published,
        "location": location,
        "search": search,
        "cursor": cursor,
    }


def _make_extensions(*, persisted_query: Dict[str, Any], **kw: Any) -> Dict[str, Any]:
    return {"persistedQuery": persisted_query, **kw}


def _make_persisted_query(*, version: int = 1, sha_256_hash: str) -> Dict[str, Any]:
    return {"version": version, "sha256Hash": sha_256_hash}


def _make_query(
    operation_name: str, variables: Dict[str, Any], extensions: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "operationName": operation_name,
        "variables": variables,
        "extensions": extensions,
    }


def _make_headers(app_id: str, uid: str, splits: str) -> Dict[str, Any]:
    return {
        "Accept-Language": "ru,en;q=0.9",
        "Connection": "keep-alive",
        "Origin": "https://youla.ru",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.6.0.0 Safari/537.36",
        "accept": "*/*",
        "appId": app_id,
        "authorization": "",
        "content-type": "application/json",
        "uid": uid,
        "x-app-id": app_id,
        "x-offset-utc": "+03:00",
        "x-uid": uid,
        "x-youla-splits": splits,
    }


BRAND_TO_ID = {"iphone": "8889"}


class IterProducts(Generic[IterResult]):
    def __init__(
        self,
        provider: AsyncProvider,
        json_data: Dict[str, Any],
        headers: Dict[str, Any],
        response_class: Type[IterResult],
    ) -> None:
        self._provider = provider
        self._json_data = json_data
        self._headers = headers
        self._cursor = ""
        self._is_next_page = True
        self._response = response_class

    def __aiter__(self) -> "IterProducts[IterResult]":
        return self

    def __repr__(self) -> str:
        return f"url={self._provider.url!r}, cursor={self._cursor!r}"

    async def __anext__(self) -> IterResult:
        if not self._is_next_page:
            raise StopAsyncIteration
        self._json_data["variables"]["cursor"] = self._cursor
        response = await self._provider(
            "POST", "/graphql", json=self._json_data, headers=self._headers
        )
        result = await response.json()

        self._cursor = (
            result.get("data", {}).get("feed", {}).get("pageInfo", {}).get("cursor", "")
        )
        self._is_next_page = (
            result.get("data", {})
            .get("feed", {})
            .get("pageInfo", {})
            .get("hasNextPage", False)
        )

        return self._response(**result)

    async def collect(self) -> List[IterResult]:
        return [result async for result in self]


class YoulaAPI:
    def __init__(self, url: str = "https://api-gw.youla.ru") -> None:
        self._provider = AiohttpProvider(url)
        self._data = {"headers": {}, "city": ""}

    async def __aenter__(self) -> "YoulaAPI":
        await self._provider.__aenter__()
        data = (await self._get_data()).get("auth", {})
        self._data["headers"] = _make_headers(
            uid=data.get("uid", ""),
            app_id=data.get("apiClientId", ""),
            splits=data.get("abSplits", ""),
        )
        self._data["city"] = data.get("geoLocation", {}).get("params", {}).get("id", "")
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._provider.__aexit__(*args)

    async def _get_data(self) -> Dict[str, Any]:
        result = await self._perform_action(
            "GET",
            "https://youla.ru",
            response_class=str,
        )
        html = BeautifulSoup(result, "lxml")

        title = html.select("script")
        tag = ""
        for i in title:
            text = i.get_text(strip=True)
            if "window.__YOULA_STATE__ = " in text:
                tag = text
                break

        matched = re.search(r"\{.*?;", tag)
        done = {}
        if matched:
            done = json.loads(matched.group()[:-1])

        return done

    def iter_catalog_products_board(
        self,
        phone_brands: Optional[List[str]] = None,
        persistent_key: str = "6e7275a709ca5eb1df17abfb9d5d68212ad910dd711d55446ed6fa59557e2602",
    ) -> IterProducts[Dict[str, Any]]:
        attributes = [
            {
                "slug": "categories",
                "value": [
                    "smartfony",
                ],
                "from": None,
                "to": None,
            },
        ]

        if phone_brands:
            phone_brands = [r if r.isdigit() else BRAND_TO_ID[r] for r in phone_brands]
            attributes.insert(
                0,
                {
                    "slug": "phone_brand",
                    "value": phone_brands,
                    "from": None,
                    "to": None,
                },
            )

        json_data = _make_query(
            operation_name="catalogProductsBoard",
            variables=_make_variables(
                attributes=attributes,
                location={
                    "latitude": None,
                    "longitude": None,
                    "city": self._data["city"],
                    "distanceMax": None,
                },
            ),
            extensions=_make_extensions(
                persisted_query=_make_persisted_query(sha_256_hash=persistent_key)
            ),
        )

        return IterProducts(
            provider=self._provider,
            json_data=json_data,
            headers=self._data["headers"],  # type: ignore
            response_class=dict,
        )

    async def _perform_action(
        self,
        method: RequestMethodType,
        url_or_endpoint: str,
        *,
        response_class: Type[ResponseType],
        **kw: Any,
    ) -> Union[str, bytes, ResponseType]:
        response = await self._provider(method, url_or_endpoint, **kw)

        if issubclass(response_class, (str, bytes)):
            return response_class(await response.read())

        return response_class(**(await response.json()))
