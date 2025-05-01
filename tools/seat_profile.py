from langchain_core.tools import tool
from requestApis.seat_profile import get_seat_profile_url
from typing import Any, Optional,Dict
import traceback
@tool
async def get_seat_profile_tool(headers: Dict[str, str], dept_uuid: Optional[str] = "",) -> Any:
    """
    Get seat profile of a given department. If dept_uuid is not provided,
    it returns all seat profiles of the current company.
    passing headers.
    """
    try:
        result = await get_seat_profile_url(headers,dept_uuid)  # ✅ Properly await
        return result
    except Exception as e:
        print(e)
        traceback.print_exc()
        return f"Error fetching data: {str(e)}"