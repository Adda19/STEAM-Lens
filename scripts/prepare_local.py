"""Create local configuration without overwriting existing secrets."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parent.parent
target = root / ".env"
if not target.exists():
    source = (root / ".env.example").read_text(encoding="utf-8")
    source = source.replace("DJANGO_SECRET_KEY=\n", "DJANGO_SECRET_KEY=" + secrets.token_urlsafe(48) + "\n")
    target.write_text(source, encoding="utf-8")
    print("Created .env with a random Django secret; API key not copied.")
else:
    print("Existing .env preserved.")
# Empty imports are unnecessary and produce an extra stylesheet request.
css = root / "static/css/app.css"
css.write_text(css.read_text(encoding="utf-8").replace("@import url('');\n", ""), encoding="utf-8")
