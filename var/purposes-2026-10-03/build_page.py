"""Build review.html from the two rounds' summaries and the notes in notes.json."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

notes = json.loads((HERE / "notes.json").read_text())
html = (HERE / "page_template.html").read_text()
html = html.replace("__ROWS_AFTER__", (HERE / "summary250.json").read_text())
html = html.replace("__ROWS__", (HERE / "summary.json").read_text())
html = html.replace("__NOTES_AFTER__", json.dumps(notes["after"]))
html = html.replace("__NOTES__", json.dumps(notes["before"]))
(HERE / "review.html").write_text(html)
print(len(html))
