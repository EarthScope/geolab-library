import os
import re
import shutil
import yaml

# Configuration
target_dir = "./projects/"
output_file = "project_tiles.md"
server_js_path = "./_build/templates/site/myst/book-theme/book-theme-main/server.js"
theme_public   = "./_build/templates/site/myst/book-theme/book-theme-main/public"

INJECT_MARKER = "// tiles.js injection"
INJECT_CODE = """\
// tiles.js injection — added by generate_tiles.py
app.use(function (req, res, next) {
  var _send = res.send.bind(res);
  res.send = function (body) {
    if (typeof body === 'string' && body.includes('</head>')) {
      body = body.replace('</head>', '<script src="/tiles.js" defer></script></head>');
    }
    return _send(body);
  };
  next();
});
"""

def html_escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

# ── Load projects ────────────────────────────────────────────────────────────

items = sorted(f for f in os.listdir(target_dir) if f.endswith(('.yml', '.yaml')) and f != output_file)

projects = []
for item in items:
    try:
        with open(os.path.join(target_dir, item), encoding='utf-8') as f:
            metadata = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Skipping {item}: {e}")
        continue
    projects.append(metadata)
    print(metadata.get('title', 'No Title'))

# ── Build HTML ───────────────────────────────────────────────────────────────
# MyST sanitizes HTML content: <input>, data-* attributes, and event handlers
# are all stripped.  We therefore generate only what MyST preserves:
#   • class, style, id on div/span elements
#   • visible text content
# tiles.js (injected into the page by the patched server.js) reads class names
# and text content to drive search and tag filtering.

lines = []
lines.append('<div id="project-grid" style="display:grid;grid-template-columns:'
             'repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-top:20px;">')

for metadata in projects:
    title   = metadata.get('title',   'No Title')
    author  = metadata.get('author',  'Unknown Author')
    summary = metadata.get('summary', 'No Summary Provided')
    tags    = metadata.get('tags',    [])
    url     = metadata.get('nbgitpuller', '#')

    author_list = author if isinstance(author, list) else [author]
    author_str = ', '.join(
        f'<span class="author-pill" style="cursor:pointer;color:#0366d6;text-decoration:underline dotted;">'
        f'{html_escape(str(a))}</span>'
        for a in author_list
    )
    tag_list   = tags if isinstance(tags, list) else ([str(tags)] if tags else [])

    # class="tag-pill" is preserved by MyST; tiles.js listens for clicks on it
    tag_spans = ''.join(
        f'<span class="tag-pill" style="display:inline-block;background:#e1ecf4;color:#0366d6;'
        f'border-radius:10px;padding:2px 8px;margin:2px 2px 2px 0;font-size:0.8em;cursor:pointer;">'
        f'{html_escape(t)}</span>'
        for t in tag_list
    ) or '<span style="font-size:0.85em;color:#888;">None</span>'

    lines.append(
        f'<div class="project-card" style="border:1px solid #e1e4e8;border-radius:8px;padding:16px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.05);background:#fff;display:flex;'
        f'flex-direction:column;justify-content:space-between;">'
        f'<div>'
        f'<h3 style="margin-top:0;margin-bottom:8px;color:#0366d6;font-size:1.2em;">{html_escape(title)}</h3>'
        f'<p style="margin:0 0 12px 0;font-size:0.9em;color:#24292e;"><strong>Author:</strong> {author_str}</p>'
        f'<p style="margin:0 0 12px 0;font-size:0.9em;color:#24292e;"><strong>Summary:</strong> {html_escape(summary)}</p>'
        f'<div style="margin-top:8px;"><strong style="font-size:0.9em;">Tags:</strong><br>{tag_spans}</div>'
        f'</div>'
        f'<div style="margin-top:16px;text-align:right;">'
        f'<a href="{html_escape(url)}" target="_blank" style="text-decoration:none;background:#2ea44f;'
        f'color:white;padding:6px 12px;border-radius:6px;font-size:0.85em;font-weight:bold;'
        f'display:inline-block;">Launch</a>'
        f'</div>'
        f'</div>'
    )

lines.append('</div>')

markdown_content = "# Project Directory\n\n" + "\n".join(lines) + "\n"

with open(output_file, "w", encoding="utf-8") as f:
    f.write(markdown_content)
print(f"Generated {output_file}")