from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path
import markdown

app = Flask(__name__)
KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge_base"


def load_articles():
    articles = []

    for file in sorted(KNOWLEDGE_DIR.glob("*.md")):
        content = file.read_text(encoding="utf-8")
        content = markdown.markdown(content)
        articles.append(content)

    return articles


def init_db():
    connection = sqlite3.connect("support.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            priority TEXT,
            status TEXT DEFAULT 'Åpen'
        )
    """)
    connection.commit()
    connection.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/support", methods=["GET", "POST"])
def support():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("problem")
        category = request.form.get("category")
        priority = request.form.get("priority")
        connection = sqlite3.connect("support.db")
        
        connection.execute("""
            INSERT INTO tickets (title, description, category, priority)
            VALUES (?, ?, ?, ?)
        """, (title, description, category, priority))
        connection.commit()
        connection.close()
        return redirect(url_for("tickets"))


    return render_template("support.html")


@app.route("/tickets", methods=["GET", "POST"])
def tickets():
    search = request.args.get("search", "")
    status_filter = request.args.get("status", "")
    category_filter = request.args.get("category", "")

    if request.method == "POST":
        status = request.form.get("status")
        ticket_id = request.form.get("ticket_id")

        if ticket_id and ticket_id.isdigit():
            ticket_id = int(ticket_id)
        else:
            ticket_id = None


        print("Saksnummer:", ticket_id)
        print("Ny status:", status)
        valid_statuses = ["Åpen", "Under arbeid", "Løst"]

        if status in valid_statuses and ticket_id is not None:
            
            connection = sqlite3.connect("support.db")
            connection.execute(
                "UPDATE tickets SET status = ? WHERE id = ?",
                (status, ticket_id)
            )
            connection.commit()
            connection.close()
            return redirect(url_for("tickets"))

        else:
            print("Ugyldig status eller saksnummer!")


    connection = sqlite3.connect("support.db")

    if status_filter and status_filter not in ["Åpen", "Under arbeid", "Løst"]:
        status_filter = ""

    valid_categories = ["network", "software", "hardware", "account", "other"]

    if category_filter and category_filter not in valid_categories:
        category_filter = ""

    
    
    tickets = connection.execute(
        """
        SELECT * FROM tickets
        WHERE title LIKE ?
        AND (? = '' OR status = ?)
        AND (? = '' OR category = ?)
        ORDER BY id DESC
        """,
        (
            f"%{search}%",
            status_filter,
            status_filter,
            category_filter,
            category_filter
        )
    ).fetchall()


        
    connection.close()

    return render_template("tickets.html", tickets=tickets)



@app.route("/knowledge")
def knowledge():
    articles = load_articles()
    return render_template("knowledge.html", articles=articles)
