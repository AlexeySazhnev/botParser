from __future__ import annotations

import asyncio
import json
import ssl
from http import HTTPStatus
from typing import (
    Any,
    AsyncIterator,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

import certifi
from aiohttp import (
    BasicAuth,
    ClientError,
    ClientResponse,
    ClientSession,
    TCPConnector,
)

from src.common.async_provider import errors as err
from src.common.async_provider.base import DEFAULT_CHUNK_SIZE, AsyncProvider
from src.common.async_provider.response import Response
from src.common.async_provider.types import RequestMethodType

_ProxyBasic = Union[str, Tuple[str, BasicAuth]]
_ProxyChain = Iterable[_ProxyBasic]
_ProxyType = Union[_ProxyChain, _ProxyBasic]


def _retrieve_basic(basic: _ProxyBasic) -> Dict[str, Any]:
    from aiohttp_socks.utils import parse_proxy_url  # type: ignore

    proxy_auth: Optional[BasicAuth] = None

    if isinstance(basic, str):
        proxy_url = basic
    else:
        proxy_url, proxy_auth = basic

    proxy_type, host, port, username, password = parse_proxy_url(proxy_url)
    if isinstance(proxy_auth, BasicAuth):
        username = proxy_auth.login
        password = proxy_auth.password

    return {
        "proxy_type": proxy_type,
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "rdns": True,
    }


def _prepare_connector(
    chain_or_plain: _ProxyType,
) -> Tuple[Type[TCPConnector], Dict[str, Any]]:
    from aiohttp_socks import (  # type: ignore
        ChainProxyConnector,
        ProxyConnector,
        ProxyInfo,
    )

    if isinstance(chain_or_plain, str) or (
        isinstance(chain_or_plain, tuple) and len(chain_or_plain) == 2
    ):
        chain_or_plain = cast(_ProxyBasic, chain_or_plain)
        return ProxyConnector, _retrieve_basic(chain_or_plain)

    chain_or_plain = cast(_ProxyChain, chain_or_plain)
    infos: List[ProxyInfo] = []
    for basic in chain_or_plain:
        infos.append(ProxyInfo(**_retrieve_basic(basic)))

    return ChainProxyConnector, {"proxy_infos": infos}


class ClientResponseAdapter(Response):
    __slots__ = (
        "_raw_content",
        "_origin_response",
    )

    def __init__(self, origin_response: ClientResponse, raw_content: bytes) -> None:
        self._origin_response = origin_response
        self._raw_content = raw_content

    def __repr__(self) -> str:
        return f"{type(self).__name__}(url={self.url!r}, status={self.status!r})"

    async def __aenter__(self) -> ClientResponseAdapter:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._origin_response.__aexit__(*args)

    async def json(self, **kwargs: Any) -> Any:
        encoding = kwargs.pop("encoding", "utf-8")
        stripped = self._raw_content.strip()
        return json.loads(stripped.decode(encoding), **kwargs)

    async def read(self) -> bytes:
        # returns it unchanged
        return self._raw_content

    async def text(self, **kwargs: Any) -> str:
        encoding, errors = (
            kwargs.get("encoding", "utf-8"),
            kwargs.get("errors", "strict"),
        )
        return self._raw_content.decode(encoding=encoding, errors=errors)

    @property
    def status(self) -> int:
        return self._origin_response.status

    @property
    def url(self) -> str:
        return self._origin_response.url.human_repr()

    @property
    def headers(self) -> Mapping[str, Any]:
        return self._origin_response.headers

    @property
    def cookies(self) -> Mapping[str, Any]:
        return self._origin_response.cookies


async def _check_response(response: ClientResponse) -> Response:
    status_code = response.status
    content = await response.read()
    if HTTPStatus.OK <= status_code <= HTTPStatus.IM_USED:
        return ClientResponseAdapter(response, content)

    url = response.url.human_repr()
    if status_code == HTTPStatus.BAD_REQUEST:
        raise err.BadRequestError(
            status_code=status_code, content=content, message="Bad request", url=url
        )
    if status_code == HTTPStatus.TOO_MANY_REQUESTS:
        raise err.TooManyRequestsError(
            status_code=status_code,
            content=content,
            message="Too many requests",
            url=url,
        )
    if status_code == HTTPStatus.NOT_FOUND:
        raise err.NotFoundError(
            status_code=status_code, content=content, message="Not found", url=url
        )
    if status_code == HTTPStatus.CONFLICT:
        raise err.ConflictError(
            status_code=status_code, content=content, message="Conflict", url=url
        )
    if status_code == HTTPStatus.UNAUTHORIZED:
        raise err.UnauthorizedError(
            status_code=status_code,
            content=content,
            message="Auth is required",
            url=url,
        )
    if status_code == HTTPStatus.FORBIDDEN:
        raise err.ForbiddenError(
            status_code=status_code,
            content=content,
            message="You have no permissions",
            url=url,
        )
    if status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE:
        raise err.EntityTooLarge(
            status_code=status_code,
            content=content,
            message="Too large content",
            url=url,
        )
    if status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        raise err.ServerError(
            status_code=status_code,
            content=content,
            message="Server is disabled or you are banned",
            url=url,
        )

    raise err.APIError(
        status_code=status_code, content=content, message="Unknown Error", url=url
    )


class AiohttpProvider(AsyncProvider):
    __slots__ = (
        "_session",
        "_connector_type",
        "_connector_init",
        "_should_reset_connector",
        "_proxy",
        "_kw",
    )

    def __init__(
        self, url: Optional[str] = None, proxy: Optional[_ProxyType] = None, **kw: Any
    ) -> None:
        super().__init__(url)
        self._session: Optional[ClientSession] = None
        self._connector_type: Type[TCPConnector] = TCPConnector
        self._connector_init: Dict[str, Any] = {
            "ssl": ssl.create_default_context(cafile=certifi.where())
        }
        self._should_reset_connector = True
        self._proxy = proxy
        self._kw = kw
        if proxy is not None:
            try:
                self._setup_proxy_connector(proxy)
            except ImportError as exc:
                raise RuntimeError(
                    "In order to use aiohttp client for proxy requests, install "
                    "https://pypi.org/project/aiohttp-socks/"
                ) from exc

    @property
    def proxy(self) -> Optional[_ProxyType]:
        return self._proxy

    @proxy.setter
    def proxy(self, value: _ProxyType) -> None:
        self._setup_proxy_connector(value)
        self._should_reset_connector = True

    async def create_session(self) -> ClientSession:
        if self._should_reset_connector:
            await self.close_session()

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=self._connector_type(**self._connector_init), **self._kw
            )
            self._should_reset_connector = False

        return self._session

    async def close_session(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def make_request(
        self, method: RequestMethodType, url_or_endpoint: str = "", **kw: Any
    ) -> Response:
        session = await self.create_session()

        try:
            async with await session.request(
                method=method, url=self._resolve_url(url_or_endpoint), **kw
            ) as response:
                return await _check_response(response)
        except asyncio.TimeoutError as e:
            raise err.NetworkError("Request timeout error") from e
        except ClientError as e:
            raise err.NetworkError(f"{type(e).__name__} occurred") from e

    async def stream_content(
        self,
        url_or_endpoint: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        raise_for_status: bool = True,
        **kw: Any,
    ) -> AsyncIterator[bytes]:
        session = await self.create_session()
        async with session.get(
            self._resolve_url(url_or_endpoint), raise_for_status=raise_for_status, **kw
        ) as resp:
            async for chunk in resp.content.iter_chunked(chunk_size):
                yield chunk

    def update_cookies(self, values: Mapping[str, Any]) -> None:
        if not self._session:
            raise TypeError("Cannot update headers while session is not connected")
        elif self._session and self._session.closed:
            raise TypeError("Cannot update headers while session disconnected")
        self._session.cookie_jar.update_cookies(values)

    def update_headers(self, values: Mapping[str, Any]) -> None:
        if not self._session:
            raise TypeError("Cannot update headers while session is not connected")
        elif self._session and self._session.closed:
            raise TypeError("Cannot update headers while session disconnected")
        self._session.headers.update(values)

    def _resolve_url(self, url_or_endpoint: str) -> str:
        if url_or_endpoint.startswith("http"):
            url = url_or_endpoint
        else:
            if not self.url:
                raise ValueError("If you want to use endpoints you should provide url.")
            url = self.url + url_or_endpoint

        return url

    def _setup_proxy_connector(self, proxy: _ProxyType) -> None:
        self._connector_type, self._connector_init = _prepare_connector(proxy)
        self._proxy = proxy
