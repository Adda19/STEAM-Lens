from pathlib import Path
root = Path(__file__).resolve().parent.parent
for name, lines in [("requirements.txt", ["reportlab>=5.0,<6", "pypdf>=6.18,<7"]),
                    (".env.example", ["TELEGRAM_BOT_TOKEN="]), (".gitignore", [".runtime/"])]:
    path = root / name
    text = path.read_text(encoding="utf-8")
    for line in lines:
        if line not in text.splitlines():
            text = text.rstrip() + "\n" + line + "\n"
    path.write_text(text, encoding="utf-8")
print("Telegram dependencies and example configuration documented; existing .env unchanged.")
