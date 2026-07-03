"""Build the static blog from content/posts/*.md into dist/."""

import datetime
import shutil
from pathlib import Path

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content" / "posts"
STATIC_DIR = ROOT / "static"
TEMPLATES_DIR = ROOT / "templates"
DIST_DIR = ROOT / "dist"

MD_EXTENSIONS = ["fenced_code", "codehilite", "tables"]


class BlogPost:
    def __init__(self, path: Path):
        post = frontmatter.load(path)
        self.title = post["title"]
        self.slug = post.get("slug", path.stem)
        date = post["date"]
        if isinstance(date, datetime.datetime):
            date = date.date()
        self.date = date
        self.html = markdown.markdown(post.content, extensions=MD_EXTENSIONS)


def load_posts() -> list[BlogPost]:
    posts = [BlogPost(path) for path in sorted(CONTENT_DIR.glob("*.md"))]
    posts.sort(key=lambda p: p.date, reverse=True)
    return posts


def build():
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    posts = load_posts()
    year = datetime.date.today().year

    index_tpl = env.get_template("index.html")
    (DIST_DIR / "index.html").write_text(
        index_tpl.render(posts=posts, root="", year=year)
    )

    post_tpl = env.get_template("post.html")
    for post in posts:
        post_dir = DIST_DIR / "posts" / post.slug
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(
            post_tpl.render(post=post, root="../../", year=year)
        )

    shutil.copytree(STATIC_DIR, DIST_DIR / "static")

    print(f"Built {len(posts)} post(s) into {DIST_DIR}")


if __name__ == "__main__":
    build()
