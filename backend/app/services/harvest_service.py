from datetime import datetime

import httpx

from app.schemas.harvest import HarvestArticle


def restore_abstract(abstract_index: dict | None) -> str | None:
    if not abstract_index:
        return None

    positions = []
    for word, pos_list in abstract_index.items():
        for pos in pos_list:
            positions.append((pos, word))

    positions.sort()
    return " ".join(word for _, word in positions)


async def search_openalex(query: str, years: int = 2) -> list[HarvestArticle]:
    current_year = datetime.now().year
    from_year = current_year - years + 1

    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "filter": f"from_publication_date:{from_year}-01-01",
        "per-page": 10,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    results = []

    for item in data.get("results", []):
        title = item.get("title") or "No title"

        authors = []
        for authorship in item.get("authorships", []):
            author = authorship.get("author", {})
            name = author.get("display_name")
            if name:
                authors.append(name)

        year = item.get("publication_year")

        journal = None
        primary_location = item.get("primary_location")
        if primary_location and primary_location.get("source"):
            journal = primary_location["source"].get("display_name")

        doi = item.get("doi")
        url = item.get("id")
        openalex_id = item.get("id") or ""
        cited_by_count = item.get("cited_by_count")
        abstract = restore_abstract(item.get("abstract_inverted_index"))

        results.append(
            HarvestArticle(
                openalex_id=openalex_id,
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                doi=doi,
                url=url,
                abstract=abstract,
                cited_by_count=cited_by_count,
            )
        )

    return results


async def get_openalex_work_by_id(openalex_id: str) -> dict:
    # Берем только ID (W4414849058)
    work_id = openalex_id.split("/")[-1]

    url = f"https://api.openalex.org/works/{work_id}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()