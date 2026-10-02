from threading import Lock

from app.schemas import Comic


_comics: dict[str, Comic] = {}

_lock = Lock()


def save_comic(comic: Comic) -> None:
    with _lock:
        _comics[comic.comic_id] = comic


def get_comic(comic_id: str) -> Comic | None:
    with _lock:
        return _comics.get(comic_id)