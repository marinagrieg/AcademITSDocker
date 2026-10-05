import os
from flask import Flask, request, redirect, render_template_string
import psycopg

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Мои заметки</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 700px; margin: 50px auto; }
        h1 { margin-bottom: 25px; }
        form { display: flex; gap: 10px; margin-bottom: 25px; }
        input { flex: 1; padding: 10px; font-size: 16px; }
        button { padding: 10px 18px; cursor: pointer; }
        li { margin: 10px 0; padding: 12px; background: #f2f2f2; border-radius: 6px; }
    </style>
</head>
<body>
    <h1>📝 Мои заметки</h1>

    <form method="post" action="/notes">
        <input name="text" placeholder="Введите заметку..." required>
        <button type="submit">Добавить</button>
    </form>

    <ul>
    {% for note in notes %}
        <li>{{ note[1] }}</li>
    {% else %}
        <li>Заметок пока нет.</li>
    {% endfor %}
    </ul>
</body>
</html>
"""

def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "myapp"),
        user=os.getenv("DB_USER", "myuser"),
        password=os.getenv("DB_PASSWORD", "mypassword"),
    )

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL
                )
            """)

@app.get("/")
def index():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, text FROM notes ORDER BY id DESC")
            notes = cur.fetchall()
    return render_template_string(HTML, notes=notes)

@app.post("/notes")
def add_note():
    text = request.form.get("text", "").strip()
    if text:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO notes (text) VALUES (%s)", (text,))
    return redirect("/")

@app.get("/health")
def health():
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
        return "OK", 200
    except Exception:
        return "Database unavailable", 503

if __name__ == "__main__":
    import time
    for _ in range(30):
        try:
            init_db()
            break
        except Exception:
            time.sleep(1)

    app.run(host="0.0.0.0", port=8000)