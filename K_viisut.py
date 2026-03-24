from flask import Flask, render_template, redirect, url_for, session, request
import json
import os


app = Flask(__name__)
app.secret_key = "supersecretkey"
PASSWORD = "Jormakka"
USERS = ["Jura", "Mirko", "Patrik", "Riko", "Tuomas"]
POINTS = [12, 10, 8, 7, 6, 5, 4, 3, 2, 1]

SONGS = [
    {"id": 1, "title": "Paspartuu", "file": "Paspartuu klippi.mp3"},
    {"id": 2, "title": "Jyrki feat. Neponen", "file": "Jyrki feat. Neponen klippi.mp3"},
    {"id": 3, "title": "Kapselihuoneen Kaapo", "file": "Kapselihuoneen Kaapo klippi.mp3"},
    {"id": 4, "title": "Kaksi naamaa", "file": "Kaksi naamaa klippi.mp3"},
    {"id": 5, "title": "Jåger Mazer", "file": "Jåger Mazer klippi.mp3"}
]

if not os.path.exists("rankings.json"):
    with open("rankings.json", "w") as f:
        f.write("{}")

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

    ranking = request.json.get("ranking")  # list of song IDs

    with open("rankings.json", "r") as f:
        data = json.load(f)

    data[user] = ranking

    with open("rankings.json", "w") as f:
        json.dump(data, f, indent=2)

    return {"status": "ok"}

@app.route("/get-ranking")
def get_ranking():
    user = session.get("user")

    try:
        with open("rankings.json", "r") as f:
            data = json.load(f)
    except:
        data = {}

    if not user:
        return {"ranking": []}

    return {"ranking": data.get(user, [])}

@app.route("/results")
def results():
    with open("rankings.json") as f:
        rankings = json.load(f)

    scores = {}

    for user, ranking in rankings.items():
        for i, song_id in enumerate(ranking):
            if i >= len(POINTS):
                break

            points = POINTS[i]
            scores[song_id] = scores.get(song_id, 0) + points

    return scores




# Remove this entirely for Render
if __name__ == "__main__":
     port = int(os.environ.get("PORT", 5000))  # default to 5000 locally
     app.run(host="0.0.0.0", port=port) # debug=True