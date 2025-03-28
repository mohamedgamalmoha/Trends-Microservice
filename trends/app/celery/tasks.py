from typing import List, Dict, Any

import httpx
from celery import shared_task, chain
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError

from app.core.conf import settings
from app.schemas.task import PropertyEnum
from app.exceptions import TrendRequestFailed
from app.celery.base_task import TrendTask


@shared_task(
    queue='trends_queue',
    routing_key='trends_routing_key',
    exchange='trends_exchange',
    base=TrendTask,
    throws=(TrendRequestFailed, ),
    autoretry_for=(TrendRequestFailed, ),
    max_retries=5,
    default_retry_delay=5
)
def trends_search_task(
        q: str | List[str],
        geo: str | None = None,
        time: str | None = None,
        cat: int | None = None,
        gprop: PropertyEnum | None = None,
        tz: int | None = None
    ) -> List[Dict[str, Any]]:
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
    try:
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
            'geo': '',
            'timeframe': 'today 5-y',  # Default to 5 years if not specified
            'cat': 0,
            'gprop': ''
        }

        # Add optional parameters
        if geo:
            payload_params['geo'] = geo
        if time:
            payload_params['timeframe'] = time
        if cat:
            payload_params['cat'] = cat
        if gprop and gprop != 'web':  # Default is 'web', so only set if not 'web'
            payload_params['gprop'] = gprop

        # Build the payload
        pytrends.build_payload(**payload_params)

        # Fetch interest over time
        interest_over_time_df = pytrends.interest_over_time()

        # Convert DataFrame to list of dictionaries
        interest_over_time_list = interest_over_time_df.reset_index().to_dict('records')

    except ResponseError:
        raise TrendRequestFailed("Failed to fetch Google Trends data")
    else:
        # Prepare results dictionary
        results = []
        for interest in interest_over_time_list:
            results.append({
                "date": interest["date"].isoformat(),
                "is_partial": interest["isPartial"],
                "q_list": [
                    {"query": ky, "value": interest[ky]} for ky in interest.keys() if ky not in ["date", "isPartial"]
                ]
            })
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
