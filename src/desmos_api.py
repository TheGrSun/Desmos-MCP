import os
import httpx
from typing import Optional, List

# 从环境变量中获取 API 密钥，如果未设置则为空
API_KEY = os.environ.get("DESMOS_API_KEY")
API_BASE_URL = "https://www.desmos.com/api/v1.11/"

class DesmosAPIClient:
    """A client for interacting with the Desmos API."""

    def __init__(self, api_key: str = API_KEY):
        if not api_key:
            raise ValueError("Desmos API key is not set. Please set the DESMOS_API_KEY environment variable.")
        self.api_key = api_key

    async def plot_formula(self, formula: str, x_range: List[float], y_range: List[float]) -> Optional[bytes]:
        """Requests a plot from the Desmos API and returns the image bytes."""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        # 注意：此处的 payload 结构是基于通用 API 设计的推断，可能需要根据实际的 Desmos API 文档进行调整
        payload = {
            "formula": formula,
            "x_range": x_range,
            "y_range": y_range,
            "format": "png"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{API_BASE_URL}/plot", headers=headers, json=payload, timeout=15.0)
                response.raise_for_status() # 如果状态码是 4xx 或 5xx，则引发异常
                return response.content
            except httpx.HTTPStatusError as e:
                print(f"Desmos API returned an error: {e.response.status_code} {e.response.text}")
                return None
            except httpx.RequestError as e:
                print(f"Error connecting to Desmos API: {e}")
                return None
