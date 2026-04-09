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

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    try:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    except Exception as e:
        print("DB connection error:", e)
        return None

def init_db():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS rankings (
                        user_name TEXT PRIMARY KEY,
                        ranking JSON
                    );
                """)
                conn.commit()
    except Exception as e:
        print("DB init failed:", e)

SONGS = [
    {"id": 10, "title": "Mä elän", "artist": "Ahmis Zoni", "country": "cu.png",
     "file": "Ahmis Zoni, Mä elän klippi.mp3", "full_file": "Ahmis Zoni, Mä elän.mp3"},
    {"id": 6, "title": "Mun tunteet", "artist": "Barracks O'Bama", "country": "us.png",
     "file": "Barracks OBama klippi.mp3", "full_file": "Barracks OBama.mpeg"},
    {"id": 12, "title": "DeathMetalPate", "artist": "Chile", "country": "cl.png", "file": "Chile, DeathMetalPate klippi.mp3", "full_file": "Chile, DeathMetalPate.mp3"},
{"id": 16, "title": "OG-Pate", "artist": "Chile", "country": "cl.png", "file": "Chile, OG-Pate klippi.mp3", "full_file": "Chile, OG-Pate.mp3"},
    {"id": 15, "title": "Cha Cha Cha", "artist": "Käärijä", "country": "fi.png", "file": "Käärijä, Cha Cha Cha klippi.mp3", "full_file": "Käärijä, Cha Cha Cha.mp3"},
    {"id": 13, "title": "Leipuri Hiiva", "artist": "Costa Rica", "country": "cr.png", "file": "Costa Rica, Leipuri Hiiva klippi.mp3", "full_file": "Costa Rica, Leipuri Hiiva.mp3"},
    {"id": 14, "title": "Kusi noussu hattuun taas", "artist": "Deata", "country": "it.png", "file": "Deata, Kusi noussu hattuun taas, Italia klippi.mp3", "full_file": "Deata, Kusi noussu hattuun taas, Italia.mp3"},
    {"id": 2, "title": "Kynitty", "artist": "Jyrki feat. Neponen", "country": "qa.png",
     "file": "Jyrki feat. Neponen klippi.mp3", "full_file": "Jyrki feat. Neponen - Kynitty, Qatar.mpeg"},
    {"id": 5, "title": "Ikean lihapulla", "artist": "Jåger Mazer", "country": "se.png",
     "file": "Jåger Mazer klippi.mp3", "full_file": "Jåger Mazer - Ikean lihapulla, Ruotsi.mpeg"},
    {"id": 7, "title": "Nyt lähtee nirri", "artist": "Kaapon ystävät", "country": "ar.png",
     "file": "Kaapon ystävät, Nyt lähtee nirri klippi.mp3", "full_file": "Kaapon ystävät, Nyt lähtee nirri.mpeg"},
    {"id": 3, "title": "Muukalainen", "artist": "Kapselihuoneen Kaapo", "country": "saturn.png",
     "file": "Kapselihuoneen Kaapo klippi.mp3", "full_file": "Kapselihuoneen Kaapo - Muukalainen, Avaruus.mpeg"},
    {"id": 8, "title": "Tässä on eteläafrikkalaisen selkäranka", "artist": "Kyrillos Turpaanvetajaios",
     "country": "cy.png", "file": "Kyrillos, Tässä on Eteläafrikkalaisen selkäranka klippi.mp3",
     "full_file": "Kyrillos, Tässä on Eteläafrikkalaisen selkäranka.mpeg"},
    {"id": 11, "title": "Neuvostoliiton kansallislaulu", "artist": "Paavi", "country": "sg.png", "file": "Paavi, Neuvostoliiton kansallislaulu klippi.mp3", "full_file": "Paavi, Neuvostoliiton kansallislaulu.mp3"},
    {"id": 1, "title": "Kyrsäkosken kasvatti", "artist": "Paspartuu", "country": "fr.png", "file": "Paspartuu klippi.mp3", "full_file": "Paspartuu - Kyrsäkosken kasvatti, Ranska.mpeg"},
    {"id": 9, "title": "Olé", "artist": "Polle", "country": "lv.png", "file": "Polle, Ole klippi.mp3", "full_file": "Polle, Ole.mpeg"},
    {"id": 4, "title": "Kaksi naamaa", "artist": "Valko-Venäjä", "country": "by.png", "file": "Kaksi naamaa klippi.mp3",
     "full_file": "Valko-Venäjä Kaksi naamaa.mpeg"}


]
#{"id": , "title": "", "artist": "", "country": "", "file": "", "full_file": ""}





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

    init_db()

    return render_template(
        "app.html",
        user=session["user"],
        songs=SONGS,
        users=USERS
    )


@app.route("/save-ranking", methods=["POST"])
def save_ranking():
    user = session.get("user")
    if not user:
        return {"error": "Not logged in"}, 403

    ranking = request.json.get("ranking")

    conn = get_conn()
    if not conn:
        return {"error": "Database unavailable"}, 500

    with conn:
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

    conn = get_conn()
    if not conn:
        return {"error": "Database unavailable"}, 500

    with conn:
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

    conn = get_conn()
    if not conn:
        return {"error": "Database unavailable"}, 500

    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ranking FROM rankings")
            all_rankings = cur.fetchall()

    for (ranking,) in all_rankings:
        for i, song_id in enumerate(ranking):
            if i >= len(POINTS):
                break
            scores[song_id] = scores.get(song_id, 0) + POINTS[i]
            #scores[13] = scores.get(song_id, 0) + POINTS[i] + 10000 #Aprillipila


    # Convert to full song data
    result_list = []
    for song in SONGS:
        total = scores.get(song["id"], 0)
        result_list.append({
            "id": song["id"],
            "title": song["title"],
            "artist": song["artist"],
            "country": song["country"],
            "points": total
        })

    # Sort descending by points
    result_list.sort(key=lambda x: x["points"], reverse=True)

    return render_template("results.html", results=result_list)

@app.route("/user-results/<username>")
def user_results(username):
    if username not in USERS:
        return "Invalid user"

    conn = get_conn()
    if not conn:
        return {"error": "Database unavailable"}, 500

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ranking FROM rankings WHERE user_name = %s
            """, (username,))
            result = cur.fetchone()

    if not result:
        return render_template(
            "app.html",
            user=session["user"],
            songs=SONGS,
            users=USERS
        )

    ranking = result[0]

    # Build song list with points
    result_list = []
    for i, song_id in enumerate(ranking):
        song = next((s for s in SONGS if s["id"] == song_id), None)
        if not song:
            continue

        points = POINTS[i] if i < len(POINTS) else 0

        result_list.append({
            "artist": song["artist"],
            "title": song["title"],
            "country": song["country"],
            "points": points
        })

    return render_template(
        "user_results.html",
        results=result_list,
        username=username
    )

@app.route("/full-songs")
def full_songs():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    return render_template(
        "full_songs.html",
        songs=SONGS
    )



if __name__ == "__main__":
     port = int(os.environ.get("PORT", 5000))  # default to 5000 locally
     app.run(host="0.0.0.0", port=port) # debug=True