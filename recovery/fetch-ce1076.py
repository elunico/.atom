import asyncio
from typing import Dict


async def fetch(
    url: str,
    method: str = 'GET',
    mode: str = 'cors',
    cache: str = 'default',
    credentials: str = 'same-origin',
    headers: Dict[str, str] = dict(),
    redirect: str = 'follow',
    referrerPolicy: str = 'no-referrer-when-downgrade',
    body: str = ''
) -> 'Promise':
    return 'hello'
