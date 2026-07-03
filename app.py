import os
import sqlite3
from pathlib import Path
from flask import Flask, g, redirect, render_template, request, url_for, abort

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "leggi_del_bang.db"))
CARD_TYPES = ("LEI", "DOURADA", "VERDE", "AZUL")


def get_db():
    if "db" not in g:
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        with open(BASE_DIR / "schema.sql", encoding="utf-8") as file:
            connection.executescript(file.read())
        connection.commit()
    finally:
        connection.close()


def normalize_form_data(form):
    card_type = form.get("type", "").strip().upper()
    name = form.get("name", "").strip()
    description = form.get("description", "").strip()
    creator = form.get("creator", "").strip()

    errors = []
    if card_type not in CARD_TYPES:
        errors.append("Tipo de carta inválido.")
    if not name:
        errors.append("O nome da carta é obrigatório.")
    if not description:
        errors.append("A descrição da carta é obrigatória.")
    if len(description) > 128:
        errors.append("A descrição deve ter no máximo 128 caracteres.")
    if not creator:
        errors.append("O nome do criador é obrigatório.")

    return {
        "type": card_type,
        "name": name,
        "description": description,
        "creator": creator,
    }, errors


def get_card_or_404(card_id):
    card = get_db().execute(
        "SELECT id, name, description, creator, type, created_at, updated_at FROM carta WHERE id = ?",
        (card_id,),
    ).fetchone()

    if card is None:
        abort(404)

    return card


@app.route("/")
def home():
    return redirect(url_for("list_cards"))


@app.route("/cartas")
def list_cards():
    cards = get_db().execute(
        """
        SELECT id, name, description, creator, type, created_at, updated_at
        FROM carta
        ORDER BY created_at DESC, id DESC
        """
    ).fetchall()
    return render_template("cards.html", cards=cards)


@app.route("/cartas/nova", methods=("GET", "POST"))
def create_card():
    card = {"type": "LEI", "name": "", "description": "", "creator": ""}
    errors = []

    if request.method == "POST":
        card, errors = normalize_form_data(request.form)

        if not errors:
            get_db().execute(
                """
                INSERT INTO carta (name, description, creator, type)
                VALUES (?, ?, ?, ?)
                """,
                (card["name"], card["description"], card["creator"], card["type"]),
            )
            get_db().commit()
            return redirect(url_for("list_cards"))

    return render_template("create_card.html", card=card, errors=errors, card_types=CARD_TYPES)


@app.route("/cartas/<int:card_id>/editar", methods=("GET", "POST"))
def edit_card(card_id):
    existing_card = get_card_or_404(card_id)
    card = dict(existing_card)
    errors = []

    if request.method == "POST":
        card, errors = normalize_form_data(request.form)
        card["id"] = card_id

        if not errors:
            get_db().execute(
                """
                UPDATE carta
                SET name = ?, description = ?, creator = ?, type = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (card["name"], card["description"], card["creator"], card["type"], card_id),
            )
            get_db().commit()
            return redirect(url_for("list_cards"))

    return render_template("edit_card.html", card=card, errors=errors, card_types=CARD_TYPES)


@app.route("/cartas/<int:card_id>/excluir", methods=("POST",))
def delete_card(card_id):
    get_card_or_404(card_id)
    get_db().execute("DELETE FROM carta WHERE id = ?", (card_id,))
    get_db().commit()
    return redirect(url_for("list_cards"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
else:
    init_db()
