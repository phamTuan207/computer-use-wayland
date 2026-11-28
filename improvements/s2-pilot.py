#!/usr/bin/env python3
"""S2 pilot: Fetcher-only Scrapling crawl.
Targets: Hacker News front page + top 10 threads (via official HN API for item
data) + GitHub trending (overall + Python) + GitHub API metadata for top 10.
Bounded: max 50 requests total, 1 request per 2.5s, robots.txt checked first
(HN: Crawl-delay 30, item pages allowed; GitHub: /trending not disallowed).
Public data only, learning/research only. No login, no evasion.
Output: improvements/s2-pilot-data.jsonl (one JSON record per fetch).
"""
import json
import os
import re
import time
from datetime import datetime, timezone

from scrapling.fetchers import Fetcher
from scrapling.parser import Adaptor

OUT = os.path.expanduser("~/workspace/computer-use-wayland/improvements/s2-pilot-data.jsonl")
SLEEP = 2.5
count = 0


def now():
    return datetime.now(timezone.utc).isoformat()


def fetch(url, headers=None):
    """One Fetcher request. Returns (status, body_bytes). Counts every attempt."""
    global count
    count += 1
    try:
        if headers:
            r = Fetcher.get(url, timeout=30, headers=headers)
        else:
            r = Fetcher.get(url, timeout=30)
        return r.status, r.body
    except TypeError:
        # headers kwarg not accepted, retry plain
        r = Fetcher.get(url, timeout=30)
        return r.status, r.body
    except Exception as e:
        return None, str(e).encode("utf-8", "replace")


def rec(source, url, status, data):
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(json.dumps(
            {"source": source, "url": url, "fetched_at": now(),
             "status": status, "data": data}, ensure_ascii=False) + "\n")


def sleep():
    time.sleep(SLEEP)


def el_text(el):
    try:
        return (el.get_all_text() or "").strip()
    except Exception:
        return ""


def main():
    t0 = time.time()
    open(OUT, "w").close()  # fresh file

    # 1. Hacker News front page (HTML, 1 request; crawl-delay 30 respected by
    #    making this the only HN website request, thread data comes from the API)
    status, body = fetch("https://news.ycombinator.com/")
    html = body.decode("utf-8", "replace")
    page = Adaptor(html, url="https://news.ycombinator.com/")
    titles = page.css("tr.athing .titleline > a")
    scores = page.css(".subtext .score")
    links = page.css(".subtext a")
    comment_links = [a for a in links
                     if (a.attrib.get("href") or "").startswith("item?id=")
                     and ("comment" in el_text(a) or "discuss" in el_text(a))]
    stories = []
    for i, a in enumerate(titles):
        href = a.attrib.get("href") or ""
        score = None
        if i < len(scores):
            m = re.search(r"(\d+)", el_text(scores[i]))
            score = int(m.group(1)) if m else None
        item_id = None
        comments = None
        if i < len(comment_links):
            chref = comment_links[i].attrib.get("href") or ""
            m = re.search(r"id=(\d+)", chref)
            item_id = int(m.group(1)) if m else None
            m2 = re.search(r"(\d+)\s+comment", el_text(comment_links[i]))
            comments = int(m2.group(1)) if m2 else 0
        stories.append({"rank": i + 1, "title": el_text(a), "url": href,
                        "score": score, "comments": comments, "item_id": item_id})
    rec("hn_front", "https://news.ycombinator.com/", status,
        {"stories": stories, "n_titles": len(titles), "n_scores": len(scores),
         "n_comment_links": len(comment_links)})
    print("HN front: status", status, "stories", len(stories))
    sleep()

    # 2. Top 10 threads by score, via the official HN API (public JSON, no auth)
    top = sorted([s for s in stories if s["item_id"]],
                 key=lambda s: s["score"] or 0, reverse=True)[:10]
    for s in top:
        item_url = "https://hacker-news.firebaseio.com/v0/item/%d.json" % s["item_id"]
        status, body = fetch(item_url)
        try:
            item = json.loads(body.decode("utf-8", "replace"))
        except Exception:
            item = {"parse_error": body[:200].decode("utf-8", "replace")}
        rec("hn_item", item_url, status,
            {"rank": s["rank"], "id": s["item_id"], "title": item.get("title"),
             "url": item.get("url"), "by": item.get("by"), "score": item.get("score"),
             "descendants": item.get("descendants"), "type": item.get("type"),
             "kids_n": len(item.get("kids") or [])})
        print("HN item", s["item_id"], "status", status,
              "kids", len(item.get("kids") or []))
        sleep()
        # top 2 comments, text truncated to 500 chars in the JSONL
        for kid in (item.get("kids") or [])[:2]:
            c_url = "https://hacker-news.firebaseio.com/v0/item/%d.json" % kid
            status, body = fetch(c_url)
            try:
                c = json.loads(body.decode("utf-8", "replace"))
                txt = re.sub(r"<[^>]+>", "", c.get("text") or "")[:500]
                rec("hn_comment", c_url, status,
                    {"parent": s["item_id"], "id": kid, "by": c.get("by"),
                     "text": txt})
            except Exception:
                rec("hn_comment", c_url, status,
                    {"parent": s["item_id"], "id": kid, "parse_error": True})
            print("  comment", kid, "status", status)
            sleep()

    # 3. GitHub trending, overall + Python (HTML, allowed by robots.txt)
    trending = []
    for lang, url in (("all", "https://github.com/trending"),
                      ("python", "https://github.com/trending/python?since=daily")):
        status, body = fetch(url)
        tpage = Adaptor(body.decode("utf-8", "replace"), url=url)
        rows = tpage.css("article.Box-row")
        repos = []
        for row in rows:
            a = row.css("h2 a")
            if not a:
                continue
            path = (a[0].attrib.get("href") or "").strip()
            desc = row.css("p")
            desc_t = el_text(desc[0]) if desc else ""
            lang_el = row.css('span[itemprop="programmingLanguage"]')
            lang_t = el_text(lang_el[0]) if lang_el else ""
            today = row.css("span.d-inline-block.float-sm-right")
            today_t = el_text(today[0]) if today else ""
            m = re.search(r"([\d,]+)\s+stars today", today_t)
            repos.append({"repo": path.strip("/"), "description": desc_t,
                          "language": lang_t,
                          "stars_today": int(m.group(1).replace(",", "")) if m else None})
        trending.extend(repos)
        rec("gh_trending", url, status, {"language": lang, "repos": repos})
        print("GH trending", lang, "status", status, "repos", len(repos))
        sleep()

    # 4. GitHub API metadata for the top 10 overall trending repos
    overall = [r for r in trending if r["repo"]][:10]
    gh_headers = {"Accept": "application/vnd.github+json"}
    for r in overall:
        api_url = "https://api.github.com/repos/%s" % r["repo"]
        status, body = fetch(api_url, headers=gh_headers)
        try:
            meta = json.loads(body.decode("utf-8", "replace"))
            rec("gh_repo", api_url, status,
                {"full_name": meta.get("full_name"),
                 "description": meta.get("description"),
                 "stargazers_count": meta.get("stargazers_count"),
                 "forks_count": meta.get("forks_count"),
                 "language": meta.get("language"),
                 "created_at": meta.get("created_at"),
                 "updated_at": meta.get("updated_at"),
                 "license": (meta.get("license") or {}).get("spdx_id"),
                 "topics": meta.get("topics"),
                 "open_issues_count": meta.get("open_issues_count")})
        except Exception:
            rec("gh_repo", api_url, status,
                {"repo": r["repo"], "parse_error": body[:200].decode("utf-8", "replace")})
        print("GH repo", r["repo"], "status", status)
        sleep()

    wall = time.time() - t0
    print("DONE: requests", count, "wall %.1fs" % wall)
    print("JSONL:", OUT)


if __name__ == "__main__":
    main()
