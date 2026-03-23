from flask import Flask, render_template, redirect, url_for, session, request

app = Flask(__name__)
app.secret_key = "supersecretkey"
PASSWORD = "Jormakka"


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_password = request.form.get("password")

        if entered_password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("app_page"))
        else:
            return render_template("login.html", error="Väärä salasana")

    return render_template("login.html")


@app.route("/app")
def app_page():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return "Tervetuloa!"  # we'll replace this later


if __name__ == "__main__":
    app.run(debug=True)