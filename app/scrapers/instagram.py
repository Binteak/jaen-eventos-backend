import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_VERSION = os.getenv(
    "META_GRAPH_API_VERSION",
    "v26.0",
)

GRAPH_API_URL = (
    f"https://graph.facebook.com/{GRAPH_API_VERSION}"
)


def get_instagram_config() -> dict[str, str]:
    """Lee la configuración de Instagram desde el entorno."""

    return {
        "access_token": os.getenv(
            "INSTAGRAM_ACCESS_TOKEN", ""
        ),
        "instagram_user_id": os.getenv(
            "INSTAGRAM_USER_ID", ""
        ),
        "hashtags": os.getenv(
            "INSTAGRAM_HASHTAGS",
            "jaen,jaencultura,eventosjaen",
        ),
    }


async def fetch_instagram_posts() -> list[dict[str, Any]]:
    """
    Recupera publicaciones recientes de hashtags permitidos
    mediante la API oficial de Meta.

    Todavía no determina si una publicación corresponde
    a un evento futuro: eso se añadirá en otro módulo.
    """

    config = get_instagram_config()

    access_token = config["access_token"]
    instagram_user_id = config["instagram_user_id"]

    if not access_token or not instagram_user_id:
        raise RuntimeError(
            "Falta configurar INSTAGRAM_ACCESS_TOKEN "
            "o INSTAGRAM_USER_ID en el archivo .env"
        )

    hashtags = [
        tag.strip().lstrip("#")
        for tag in config["hashtags"].split(",")
        if tag.strip()
    ]

    posts: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    async with httpx.AsyncClient(timeout=20.0) as client:
        for hashtag in hashtags:
            try:
                # 1. Obtener el ID del hashtag.
                search_response = await client.get(
                    f"{GRAPH_API_URL}/ig_hashtag_search",
                    params={
                        "user_id": instagram_user_id,
                        "q": hashtag,
                        "access_token": access_token,
                    },
                )
                search_response.raise_for_status()

                hashtag_data = search_response.json().get(
                    "data", []
                )

                if not hashtag_data:
                    continue

                hashtag_id = hashtag_data[0]["id"]

                # 2. Recuperar publicaciones recientes.
                media_response = await client.get(
                    f"{GRAPH_API_URL}/{hashtag_id}/recent_media",
                    params={
                        "user_id": instagram_user_id,
                        "fields": (
                            "id,caption,media_type,media_url,"
                            "thumbnail_url,permalink,timestamp"
                        ),
                        "limit": 25,
                        "access_token": access_token,
                    },
                )
                media_response.raise_for_status()

                for media in media_response.json().get("data", []):
                    media_id = media.get("id")

                    if not media_id or media_id in seen_ids:
                        continue

                    seen_ids.add(media_id)

                    media_type = media.get("media_type", "")
                    media_url = media.get("media_url")
                    thumbnail_url = media.get("thumbnail_url")

                    posts.append({
                        "id": media_id,
                        "title": (
                            media.get("caption", "").split("\n")[0]
                            or "Publicación de Instagram"
                        ),
                        "description": media.get("caption", ""),
                        "media_type": media_type,
                        "media_url": media_url,
                        "image_url": (
                            thumbnail_url or media_url
                            if media_type == "VIDEO"
                            else media_url
                        ),
                        "published_at": media.get("timestamp"),
                        "source_name": "Instagram",
                        "source_key": hashtag,
                        "source_url": media.get("permalink", ""),
                    })

            except httpx.HTTPStatusError as exc:
                # Un hashtag puede fallar sin detener el resto.
                print(
                    f"Error de Instagram con #{hashtag}: "
                    f"HTTP {exc.response.status_code}"
                )

            except httpx.RequestError as exc:
                print(
                    f"Error de conexión con Instagram "
                    f"para #{hashtag}: {exc}"
                )

    return posts

