from typing import List, Dict, Any

import httpx
from celery import shared_task, chain
from pytrends.request import TrendReq

from app.core.conf import settings
from app.repositories.task import update_task
from app.schemas.task import TaskUpdate
from app.schemas.query import PropertyEnum
from app.celery.base_task import TrendTask


@shared_task(
    base=TrendTask,
    max_retries=5,
    default_retry_delay=1
)
def trends_search_task(
        q: str | List[str],
        geo: str | None = None,
        time: str | None = None,
        cat: int | None = None,
        gprop: PropertyEnum | None = None,
        tz: int | None = None
    ) -> Dict[str, Any]:
    """
    Perform a Google Trends search using pytrends.

    Args:
        - q (str or List[str]): Search term(s)
        - geo (str, optional): Geographic location (e.g., 'US')
        - time (str, optional): Time range for the search
            (e.g., 'today 5-y', 'now 1-d', '2020-01-01 2021-01-01')
        - cat (int, optional): Category ID for more specific searches
        - gprop (PropertyEnum, optional): Google property to search
        - tz (int, optional): Timezone offset

    Returns:
        - Dict[str, Any]: Google Trends search results
    """
    # Initialize pytrends
    pytrends = TrendReq(
        hl='en-US',  # Language
        tz=tz or -300  # Default to Eastern Time if not specified
    )

    # Convert single string to list if needed
    keywords = q if isinstance(q, list) else [q]

    # Prepare the build payload parameters
    payload_params = {
        'kw_list': keywords,
        'timeframe': time or 'today 5-y',  # Default to 5 years if not specified
    }

    # Add optional parameters
    if geo:
        payload_params['geo'] = geo
    if cat:
        payload_params['cat'] = cat
    if gprop:
        if gprop == "web":
            gprop = ""
        payload_params['gprop'] = gprop

    # Build the payload
    pytrends.build_payload(**payload_params)

    # Prepare results dictionary
    results = {
        'interest_over_time': pytrends.interest_over_time(),
        'related_queries': pytrends.related_queries(),
        'interest_by_region': pytrends.interest_by_region(),
        'related_topics': pytrends.related_topics()
    }
    return results


@shared_task(
    max_retries=5,
    default_retry_delay=1
)
async def think_task(search_results: Dict[str, Any]) -> str:
    async with httpx.AsyncClient(timeout=settings.TIMEOUT) as client:
        response = await client.post(settings.THINK_API_URL, json=search_results)

        if response.status_code != 200:
            raise Exception(f"Failed to generate think content: {response.text}")

        result = response.json()
        return result


def trends_think_workflow(
        q: str | List[str],
        geo: str | None = None,
        time: str | None = None,
        cat: int | None = None,
        gprop: PropertyEnum | None = None,
        tz: int | None = None
    ) -> chain:

    workflow = chain(
        trends_search_task.s(q, geo, time, cat, gprop, tz),
        think_task.s()
    )

    return workflow.apply_async()
