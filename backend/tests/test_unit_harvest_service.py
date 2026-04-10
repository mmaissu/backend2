import httpx
import pytest

from app.services.harvest_service import get_openalex_work_by_id, restore_abstract, search_openalex


def test_restore_abstract_none_and_empty():
    assert restore_abstract(None) is None
    assert restore_abstract({}) is None


def test_restore_abstract_reconstructs_in_position_order():
    # inverted index format: word -> list of positions
    abstract = restore_abstract({"world": [1], "hello": [0]})
    assert abstract == "hello world"


def test_restore_abstract_handles_repeated_positions():
    abstract = restore_abstract({"a": [0, 2], "b": [1]})
    assert abstract == "a b a"


@pytest.mark.asyncio
async def test_search_openalex_parses_minimal_response(mocker):
    payload = {
        "results": [
            {
                "id": "https://openalex.org/W123",
                "title": "Paper A",
                "authorships": [{"author": {"display_name": "Alice"}}],
                "publication_year": 2024,
                "primary_location": {"source": {"display_name": "Journal X"}},
                "doi": "https://doi.org/10.1/xyz",
                "cited_by_count": 7,
                "abstract_inverted_index": {"hello": [0], "world": [1]},
            }
        ]
    }

    response = mocker.Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None

    async_client_cm = mocker.AsyncMock()
    async_client_cm.__aenter__.return_value.get = mocker.AsyncMock(return_value=response)
    async_client_cm.__aenter__.return_value.__aexit__ = mocker.AsyncMock(return_value=None)
    mocker.patch("httpx.AsyncClient", return_value=async_client_cm)

    results = await search_openalex(query="AI", years=2)
    assert len(results) == 1
    article = results[0]
    assert article.openalex_id == "https://openalex.org/W123"
    assert article.title == "Paper A"
    assert article.authors == ["Alice"]
    assert article.journal == "Journal X"
    assert article.abstract == "hello world"


@pytest.mark.asyncio
async def test_search_openalex_handles_empty_results(mocker):
    response = mocker.Mock()
    response.json.return_value = {"results": []}
    response.raise_for_status.return_value = None

    async_client_cm = mocker.AsyncMock()
    async_client_cm.__aenter__.return_value.get = mocker.AsyncMock(return_value=response)
    async_client_cm.__aenter__.return_value.__aexit__ = mocker.AsyncMock(return_value=None)
    mocker.patch("httpx.AsyncClient", return_value=async_client_cm)

    results = await search_openalex(query="anything", years=1)
    assert results == []


@pytest.mark.asyncio
async def test_search_openalex_raises_on_http_error(mocker):
    response = mocker.Mock()
    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "bad", request=mocker.Mock(), response=mocker.Mock(status_code=500)
    )

    async_client_cm = mocker.AsyncMock()
    async_client_cm.__aenter__.return_value.get = mocker.AsyncMock(return_value=response)
    async_client_cm.__aenter__.return_value.__aexit__ = mocker.AsyncMock(return_value=None)
    mocker.patch("httpx.AsyncClient", return_value=async_client_cm)

    with pytest.raises(httpx.HTTPStatusError):
        await search_openalex(query="AI", years=2)


@pytest.mark.asyncio
async def test_search_openalex_raises_on_timeout(mocker):
    async def _raise_timeout(*_args, **_kwargs):
        raise httpx.ReadTimeout("timeout", request=mocker.Mock())

    async_client_cm = mocker.AsyncMock()
    async_client_cm.__aenter__.return_value.get = mocker.AsyncMock(side_effect=_raise_timeout)
    async_client_cm.__aenter__.return_value.__aexit__ = mocker.AsyncMock(return_value=None)
    mocker.patch("httpx.AsyncClient", return_value=async_client_cm)

    with pytest.raises(httpx.ReadTimeout):
        await search_openalex(query="AI", years=2)


@pytest.mark.asyncio
async def test_get_openalex_work_by_id_strips_prefix(mocker):
    response = mocker.Mock()
    response.json.return_value = {"id": "https://openalex.org/W999"}
    response.raise_for_status.return_value = None

    get_mock = mocker.AsyncMock(return_value=response)
    async_client_cm = mocker.AsyncMock()
    async_client_cm.__aenter__.return_value.get = get_mock
    async_client_cm.__aenter__.return_value.__aexit__ = mocker.AsyncMock(return_value=None)
    mocker.patch("httpx.AsyncClient", return_value=async_client_cm)

    data = await get_openalex_work_by_id("https://openalex.org/W999")
    assert data["id"] == "https://openalex.org/W999"
    called_url = get_mock.call_args.args[0]
    assert called_url.endswith("/works/W999")

