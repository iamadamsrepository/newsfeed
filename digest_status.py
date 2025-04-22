import datetime as dt
from enum import Enum

from db.db_connection import DBHandler


class DigestStatus(Enum):
    CREATED = "CREATED"
    ARTICLES_COLLECTED = "ARTICLES_COLLECTED"
    ARTICLES_EMBEDDED = "ARTICLES_EMBEDDED"
    STORIES_GENERATED = "STORIES_GENERATED"
    STORIES_EMBEDDED = "STORIES_EMBEDDED"
    IMAGES_COLLECTED = "IMAGES_COLLECTED"
    RUNDOWNS_GENERATED = "RUNDOWNS_GENERATED"
    READY = "READY"


def add_digest_row(db: DBHandler, verbose: bool = True) -> int:
    """
    Create a new digest with the status "CREATED" and the current timestamp.
    """
    digest_id = (d if (d := db.run_sql("select max(digest_id) from stories")[0][0]) is not None else -1) + 1
    db.insert_row("digests", {"id": digest_id, "status": DigestStatus.CREATED, "ts": dt.datetime.now(dt.timezone.utc)})
    if verbose:
        print(f"Created new digest with id {digest_id} and status {DigestStatus.CREATED}")
    return digest_id


def set_digest_status(db: DBHandler, digest_id: int, status: DigestStatus, verbose: bool = True) -> None:
    """
    Set the status of a digest to one of the predefined statuses.
    """
    db.run_sql_no_return("update digests set status = %s where id = %s", (status, digest_id))
    if verbose:
        print(f"Set digest {digest_id} status to {status}")


def get_digest_status(db: DBHandler, digest_id: int) -> DigestStatus:
    """
    Get the status of a digest.
    """
    status = db.run_sql("select status from digests where id = %s", (digest_id,))
    if not status:
        raise ValueError(f"Digest with id {digest_id} does not exist.")
    return DigestStatus(status[0][0])


def get_incomplete_digest(db: DBHandler) -> tuple[int, DigestStatus]:
    """
    Get the ID and status of the most recent incomplete digest.
    """
    incomplete_digest = db.run_sql(
        "select id, status from digests where status != %s order by ts desc limit 1", (DigestStatus.READY,)
    )
    if not incomplete_digest:
        raise ValueError("No incomplete digest found.")
    return incomplete_digest[0][0], DigestStatus(incomplete_digest[0][1])
