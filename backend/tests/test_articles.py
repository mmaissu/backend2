def test_list_articles_returns_valid_structure(client):
    response = client.get("/api/articles")

    assert response.status_code == 200, response.text

    data = response.json()

    assert "items" in data
    assert "pagination" in data

    assert isinstance(data["items"], list)
    assert isinstance(data["pagination"], dict)

    pagination = data["pagination"]
    assert "page" in pagination
    assert "page_size" in pagination
    assert "total_items" in pagination
    assert "total_pages" in pagination


def test_list_articles_supports_query_params(client):
    response = client.get(
        "/api/articles?page=1&page_size=6&sort_by=newest&only_with_doi=false"
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert "items" in data
    assert "pagination" in data


def test_list_articles_invalid_page_fails(client):
    response = client.get("/api/articles?page=0")
    assert response.status_code == 422, response.text