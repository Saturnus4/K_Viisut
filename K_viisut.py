from flask import Flask, render_template, redirect, url_for, session, request
import json
import os
import logging
import psycopg2

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = "supersecretkey"
PASSWORD = "Jormakka"
USERS = ["Jura", "Mirko", "Patrik", "Riko", "Tuomas"]
POINTS = [12, 10, 8, 7, 6, 5, 4, 3, 2, 1]
DATABASE_URL = "postgresql://postgres:Gimlaskevat4@db.oxuofwapjjimjgjnsurb.supabase.co:5432/postgres"
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rankings (
            user_name TEXT PRIMARY KEY,
            ranking JSON
        );
    """)
    conn.commit()

SONGS = [
    {"id": 1, "title": "Kyrsäkosken kasvatti", "artist": "Paspartuu", "country": "fr.png", "file": "Paspartuu klippi.mp3"},
    {"id": 2, "title": "Kynitty", "artist": "Jyrki feat. Neponen", "country": "qa.png", "file": "Jyrki feat. Neponen klippi.mp3"},
    {"id": 3, "title": "Muukalainen", "artist": "Kapselihuoneen Kaapo", "country": "saturn.png", "file": "Kapselihuoneen Kaapo klippi.mp3"},
    {"id": 4, "title": "-", "artist": "Kaksi naamaa", "country": "by.png", "file": "Kaksi naamaa klippi.mp3"},
    {"id": 5, "title": "Ikean lihapulla", "artist": "Jåger Mazer", "country": "se.png", "file": "Jåger Mazer klippi.mp3"},
    {"id": 6, "title": "Mun tunteet", "artist": "Barracks O'Bama", "country": "us.png", "file": "Barracks OBama klippi.mp3"},
    {"id": 7, "title": "Nyt lähtee nirri", "artist": "Kaapon ystävät", "country": "ar.png", "file": "Kaapon ystävät, Nyt lähtee nirri klippi.mp3"},
    {"id": 8, "title": "Tässä on Eteläafrikkalaisen selkäranka", "artist": "Kyrillos Turpaanvetajaios", "country": "cy.png", "file": "Kyrillos, Tässä on Eteläafrikkalaisen selkäranka klippi.mp3"},
    {"id": 9, "title": "Olé", "artist": "Polle", "country": "lv.png", "file": "Polle, Ole klippi.mp3"},
    {"id": 10, "title": "Mä elän", "artist": "Ahmis Zoni", "country": "cu.png", "file": "Ahmis Zoni, Mä elän klippi.mp3"}

]
#{"id": , "title": "", "artist": "", "country": "", "file": ""}





@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_password = request.form.get("password")

        if entered_password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("select_user"))
        else:
            return render_template("login.html", error="Väärä salasana")

    return render_template("login.html")


@app.route("/select-user")
def select_user():
    return render_template("select_user.html", users=USERS)


@app.route("/set-user/<username>")
def set_user(username):
    if username in USERS:
        session["user"] = username
        return redirect(url_for("app_page"))

    return "Invalid user"


@app.route("/app")
def app_page():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if not session.get("user"):
        return redirect(url_for("select_user"))

    return render_template("app.html", user=session["user"], songs=SONGS)


@app.route("/save-ranking", methods=["POST"])
def save_ranking():
    user = session.get("user")
    if not user:
        return {"error": "Not logged in"}, 403

    ranking = request.json.get("ranking")

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO rankings (user_name, ranking)
            VALUES (%s, %s)
            ON CONFLICT (user_name)
            DO UPDATE SET ranking = EXCLUDED.ranking;
        """, (user, json.dumps(ranking)))

        conn.commit()

    return {"status": "ok"}

@app.route("/get-ranking")
def get_ranking():
    user = session.get("user")
    if not user:
        return {"ranking": []}

    with conn.cursor() as cur:
        cur.execute("""
            SELECT ranking FROM rankings WHERE user_name = %s
        """, (user,))
        result = cur.fetchone()

    if result:
        return {"ranking": result[0]}
    else:
        return {"ranking": []}

@app.route("/results")
def results():
    scores = {}

    with conn.cursor() as cur:
        cur.execute("SELECT ranking FROM rankings")
        all_rankings = cur.fetchall()

    for (ranking,) in all_rankings:
        for i, song_id in enumerate(ranking):
            if i >= len(POINTS):
                break

            scores[song_id] = scores.get(song_id, 0) + POINTS[i]

    return scores




# Remove this entirely for Render
if __name__ == "__main__":
     port = int(os.environ.get("PORT", 5000))  # default to 5000 locally
     app.run(host="0.0.0.0", port=port) # debug=True