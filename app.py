from flask import Flask, render_template, request, redirect, url_for
import sqlite3


app = Flask(__name__)

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
    tickets = connection.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()
    connection.close()

    return render_template("tickets.html", tickets=tickets)

