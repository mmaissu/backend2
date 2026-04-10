import pytest

from app.infrastructure.models import ArticleMetadataModel


@pytest.mark.asyncio
async def test_get_articles_empty_returns_pagination(async_client):
    resp = await async_client.get("/api/articles")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["items"] == []
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 6
    assert data["pagination"]["total_items"] == 0


@pytest.mark.asyncio
async def test_get_articles_search_and_only_with_doi(async_client, db_session):
    a1 = ArticleMetadataModel(
        openalex_id="https://openalex.org/W1",
        title="AI for Science",
        abstract=None,
        authors=["Alice"],
        doi="https://doi.org/10.1/abc",
        source="Journal A",
        cited_by_count=10,
        raw_metadata={"x": 1},
        keywords=None,
        created_by_id=None,
    )
    a2 = ArticleMetadataModel(
        openalex_id="https://openalex.org/W2",
        title="Biology Paper",
        abstract=None,
        authors=["Bob"],
        doi=None,
        source="Journal B",
        cited_by_count=1,
        raw_metadata={"x": 2},
        keywords=None,
        created_by_id=None,
    )
    db_session.add_all([a1, a2])
    await db_session.commit()

    resp = await async_client.get("/api/articles", params={"search": "ai", "only_with_doi": "true"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "AI for Science"
    assert data["items"][0]["doi"] is not None


@pytest.mark.asyncio
async def test_get_articles_sort_most_cited(async_client, db_session):
    db_session.add_all(
        [
            ArticleMetadataModel(
                openalex_id="https://openalex.org/W10",
                title="A",
                abstract=None,
                authors=[],
                doi=None,
                source=None,
                cited_by_count=2,
                raw_metadata=None,
                keywords=None,
                created_by_id=None,
            ),
            ArticleMetadataModel(
                openalex_id="https://openalex.org/W11",
                title="B",
                abstract=None,
                authors=[],
                doi=None,
                source=None,
                cited_by_count=100,
                raw_metadata=None,
                keywords=None,
                created_by_id=None,
            ),
        ]
    )
    await db_session.commit()

    resp = await async_client.get("/api/articles", params={"sort_by": "most_cited", "page_size": 50})
    assert resp.status_code == 200, resp.text
    items = resp.json()["items"]
    assert items[0]["cited_by_count"] >= items[1]["cited_by_count"]

