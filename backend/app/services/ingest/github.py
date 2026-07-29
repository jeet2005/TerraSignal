import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


GITHUB_EVENTS_URL = "https://api.github.com/events"


async def fetch_github_events(per_page: int = 100) -> List[Dict]:
    params = {"per_page": per_page}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(GITHUB_EVENTS_URL, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("github_fetch_failed", error=str(e))
            return []


GITHUB_EVENT_TYPE_MAP = {
    "PushEvent": "code_push",
    "CreateEvent": "repo_create",
    "DeleteEvent": "repo_delete",
    "ForkEvent": "fork",
    "WatchEvent": "star",
    "ReleaseEvent": "release",
    "IssuesEvent": "issue",
    "PullRequestEvent": "pull_request",
    "PullRequestReviewEvent": "pr_review",
    "CommitCommentEvent": "commit_comment",
    "IssueCommentEvent": "issue_comment",
    "GollumEvent": "wiki_edit",
    "PublicEvent": "repo_public",
}


def normalize_github_event(event: Dict) -> Optional[Event]:
    try:
        event_type = event.get("type", "")
        mapped_type = GITHUB_EVENT_TYPE_MAP.get(event_type, event_type.lower())
        
        repo = event.get("repo", {})
        actor = event.get("actor", {})
        payload = event.get("payload", {})
        
        severity = 0.05
        if event_type == "ReleaseEvent":
            severity = 0.2
        elif event_type == "ForkEvent":
            severity = 0.15
        elif event_type == "PushEvent":
            commits = payload.get("size", 0)
            severity = min(commits / 100, 0.3)
        
        return Event(
            source="github",
            domain="digital",
            event_type=mapped_type,
            severity=severity,
            geometry={"type": "Point", "coordinates": [-122.4194, 37.7749]},
            properties={
                "event_id": event.get("id"),
                "event_type": event_type,
                "repo_name": repo.get("name"),
                "repo_url": repo.get("url"),
                "actor_login": actor.get("login"),
                "actor_id": actor.get("id"),
                "payload": payload,
                "public": event.get("public"),
            },
            metadata={"severity_tier": "info"},
            timestamp=event.get("created_at", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("github_normalize_failed", error=str(e))
        return None