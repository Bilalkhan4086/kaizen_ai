import httpx
from typing import Optional, Dict
from config import BE_BASE_URL

async def get_seat_profile_url(headers: Dict[str, str], dept_uuid: Optional[str] = "") -> str:
    print("📦 Original headers:", headers)

    # Remove empty headers
    cleaned_headers = {k: v for k, v in headers.items() if v}

    base_path = "parent_job" if cleaned_headers.get("sandbox_uuid") else "job"
    url = f"{BE_BASE_URL}/{base_path}/categories_description_overview/"
    if dept_uuid:
        url += f"{dept_uuid}"

    print("🔗 Request URL:", url)
    print("📬 Cleaned headers:", cleaned_headers)

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.ReadTimeout as e:
        print(f"ReadTimeout: {e}")
        return f"Error: Request to {url} timed out."
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return f"Error: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"Error: {str(e)}"

