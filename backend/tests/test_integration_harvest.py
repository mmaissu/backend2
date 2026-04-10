import pytest


@pytest.mark.asyncio
async def test_harvest_endpoint_uses_service_and_returns_shape(async_client, mocker):
    mock_results = [
        {
            "openalex_id": "https://openalex.org/W1",
            "title": "Paper",
            "authors": ["Alice"],
            "year": 2024,
            "journal": None,
            "doi": None,
            "url": None,
            "abstract": None,
            "cited_by_count": 0,
        }
    ]

    mocker.patch("app.api.harvest.search_openalex", new=mocker.AsyncMock(return_value=mock_results))

    resp = await async_client.get("/api/harvest", params={"query": "AI", "years": 2})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["query"] == "AI"
    assert data["count"] == 1
    assert isinstance(data["results"], list)
    assert data["results"][0]["openalex_id"] == "https://openalex.org/W1"


@pytest.mark.asyncio
async def test_harvest_endpoint_validates_query_min_length(async_client):
    resp = await async_client.get("/api/harvest", params={"query": "a"})
    assert resp.status_code == 422, resp.text


@pytest.mark.asyncio
async def test_harvest_endpoint_validates_years_range(async_client):
    resp = await async_client.get("/api/harvest", params={"query": "AI", "years": 11})
    assert resp.status_code == 422, resp.text


@pytest.mark.asyncio
async def test_harvest_endpoint_returns_500_on_service_timeout(async_client, mocker):
    import httpx

    mocker.patch(
        "app.api.harvest.search_openalex",
        new=mocker.AsyncMock(side_effect=httpx.ReadTimeout("timeout")),
    )
    resp = await async_client.get("/api/harvest", params={"query": "AI", "years": 2})
    assert resp.status_code == 500, resp.text


@pytest.mark.asyncio
async def test_import_article_creates_new_row(async_client, db_session, mocker):
    from sqlalchemy import select

    from app.infrastructure.models import ArticleMetadataModel

    mocker.patch(
        "app.api.harvest.get_openalex_work_by_id",
        new=mocker.AsyncMock(
            return_value={
                "id": "https://openalex.org/W777",
                "title": "Imported Paper",
                "doi": "https://doi.org/10.1/imported",
                "cited_by_count": 5,
                "publication_date": "2024-01-02",
                "authorships": [{"author": {"display_name": "Alice"}}],
                "primary_location": {"source": {"display_name": "Journal Z"}},
                "abstract_inverted_index": {"hello": [0], "world": [1]},
            }
        ),
    )

    resp = await async_client.post("/api/harvest/import", json={"openalex_id": "https://openalex.org/W777"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["message"] == "Article imported successfully"
    assert body["article_id"]

    result = await db_session.execute(
        select(ArticleMetadataModel).where(ArticleMetadataModel.id == body["article_id"])
    )
    article = result.scalar_one()
    assert article.openalex_id == "https://openalex.org/W777"
    assert article.title == "Imported Paper"
    assert article.source == "Journal Z"
    assert article.authors == ["Alice"]
    assert article.abstract == "hello world"


@pytest.mark.asyncio
async def test_import_article_returns_existing_if_already_imported(async_client, db_session, mocker):
    from app.infrastructure.models import ArticleMetadataModel

    existing = ArticleMetadataModel(
        openalex_id="https://openalex.org/W888",
        title="Already there",
        abstract=None,
        authors=[],
        doi=None,
        source=None,
        raw_metadata={},
        keywords=None,
        created_by_id=None,
    )
    db_session.add(existing)
    await db_session.commit()
    await db_session.refresh(existing)

    mocker.patch(
        "app.api.harvest.get_openalex_work_by_id",
        new=mocker.AsyncMock(return_value={"id": "https://openalex.org/W888", "title": "Ignored"}),
    )

    resp = await async_client.post("/api/harvest/import", json={"openalex_id": "https://openalex.org/W888"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["message"] == "Article already imported"
    assert body["article_id"] == existing.id


@pytest.mark.asyncio
async def test_import_article_invalid_publication_date_sets_none(async_client, db_session, mocker):
    from sqlalchemy import select

    from app.infrastructure.models import ArticleMetadataModel

    mocker.patch(
        "app.api.harvest.get_openalex_work_by_id",
        new=mocker.AsyncMock(
            return_value={
                "id": "https://openalex.org/W999",
                "title": "Bad date",
                "publication_date": "not-a-date",
                "authorships": [],
            }
        ),
    )

    resp = await async_client.post("/api/harvest/import", json={"openalex_id": "https://openalex.org/W999"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["article_id"]

    result = await db_session.execute(
        select(ArticleMetadataModel).where(ArticleMetadataModel.id == body["article_id"])
    )
    article = result.scalar_one()
    assert article.published_at is None

