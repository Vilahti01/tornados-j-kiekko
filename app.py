import os
from sqlalchemy.ext.hybrid import hybrid_property
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)

#  Turvallisuus & Tietokanta-asetukset

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "instance", "players.db")}'

app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)

#  Admin-käyttäjän salasana
ADMIN_PASSWORD = "TornadosAdmin123"


#  Luodaan tietokanta, jos sitä ei ole
with app.app_context():
    db.create_all()

#  Funktiot API:sta ottelutietojen hakemiseen


def get_games_data():
    url = "https://tulospalvelu.leijonat.fi/helpers/getGames.php"
    payload = {
        "dwl": "0",
        "season": "2025",
        "stgid": "8723",
        "teamid": "1368626503",
        "districtid": "0",
        "gamedays": "3",
        "dog": "2025-03-17"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "X-Requested-With": "XMLHttpRequest"}

    r = requests.post(url, data=payload, headers=headers)
    try:
        data = r.json()
    except Exception as e:
        print("Error parsing JSON:", e)
        return {"upcoming": [], "played": []}

    all_games = []
    for level in data:
        if "Games" in level:
            all_games.extend(level["Games"])

    for game in all_games:
        try:
            dt = datetime.strptime(
                f"{game.get('GameDate', '')} {game.get('GameTime', '')}", "%d.%m.%Y %H:%M")
        except Exception:
            dt = None
        game["dt"] = dt
        game["result"] = f"{game.get('HomeGoals', '').strip()}-{game.get('AwayGoals', '').strip()}" if game.get(
            "HomeGoals") and game.get("AwayGoals") else "Ei tulosta"

    return {
        "upcoming": sorted([g for g in all_games if g["result"] == "Ei tulosta"], key=lambda x: x.get("dt") or datetime.max),
        "played": sorted([g for g in all_games if g["result"] != "Ei tulosta" and g.get("dt")], key=lambda x: x.get("dt") or datetime.min, reverse=True)
    }


def fetch_standings():
    url = "https://tulospalvelu.leijonat.fi/serie/helpers/getStandings.php"
    payload = {"season": "2025", "stgid": "8723"}
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "X-Requested-With": "XMLHttpRequest"}

    r = requests.post(url, data=payload, headers=headers)
    try:
        return r.json()
    except Exception as e:
        print("Error parsing standings JSON:", e)
        return {}


# Pelaajatilastojen tietokantataulu


class Player(db.Model):
    __tablename__ = 'player'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    games_played = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    penalty_minutes = db.Column(db.Integer, default=0)

    @hybrid_property
    def points(self):
        return self.goals + self.assists

    @points.expression
    def points(cls):
        return cls.goals + cls.assists  # Mahdollistaa järjestämisen tietokantakyselyissä


#  Kokoonpanon tietokantataulu


class Lineup(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Hyökkääjät (kolme ketjua, jokaisessa kolme pelaajaa)
    attack1_player1 = db.Column(db.String(255), nullable=True)
    attack1_player2 = db.Column(db.String(255), nullable=True)
    attack1_player3 = db.Column(db.String(255), nullable=True)

    attack2_player1 = db.Column(db.String(255), nullable=True)
    attack2_player2 = db.Column(db.String(255), nullable=True)
    attack2_player3 = db.Column(db.String(255), nullable=True)

    attack3_player1 = db.Column(db.String(255), nullable=True)
    attack3_player2 = db.Column(db.String(255), nullable=True)
    attack3_player3 = db.Column(db.String(255), nullable=True)

    # Puolustus (kolme paria, jokaisessa kaksi pelaajaa)
    defense1_player1 = db.Column(db.String(255), nullable=True)
    defense1_player2 = db.Column(db.String(255), nullable=True)

    defense2_player1 = db.Column(db.String(255), nullable=True)
    defense2_player2 = db.Column(db.String(255), nullable=True)

    defense3_player1 = db.Column(db.String(255), nullable=True)
    defense3_player2 = db.Column(db.String(255), nullable=True)

    # Maalivahti
    goalie = db.Column(db.String(255), nullable=True)


def get_lineup():
    lineup = Lineup.query.first()  # Hakee ensimmäisen kokoonpanon tietokannasta
    if not lineup:
        # Palauttaa tyhjät arvot, jos ei löydy
        return lineup if lineup else None

    return lineup


@app.route('/')
def index():
    # Haetaan top 3 pistemiehet
    top_players = Player.query.order_by(Player.points.desc()).limit(3).all()

    # Haetaan kokoonpano tietokannasta
    lineup = get_lineup()

    # Muodosta hyökkäysketjut Pythonissa, jotta Jinja ei tarvitse tehdä monimutkaisia operaatioita
    attack_lines = []
    defense_lines = []

    if lineup:
        attack_lines = [
            [lineup.attack1_player1, lineup.attack1_player2, lineup.attack1_player3],
            [lineup.attack2_player1, lineup.attack2_player2, lineup.attack2_player3],
            [lineup.attack3_player1, lineup.attack3_player2, lineup.attack3_player3]
        ]
        defense_lines = [
            [lineup.defense1_player1, lineup.defense1_player2],
            [lineup.defense2_player1, lineup.defense2_player2],
            [lineup.defense3_player1, lineup.defense3_player2]
        ]

    goalie = lineup.goalie if lineup else None

    # Haetaan ottelutiedot API:sta
    games_data = get_games_data()

    # Haetaan sarjataulukko API:sta
    standings = fetch_standings()

    return render_template(
        'index.html',
        top_players=top_players,
        attack_lines=attack_lines,
        defense_lines=defense_lines,
        goalie=goalie,
        lineup=lineup,
        upcoming_games=games_data.get("upcoming", []),
        standings=standings
    )

# Pelatut ottelut


@app.route('/played')
def played():
    games_data = get_games_data()
    return render_template('played.html', played_games=games_data["played"][1:])


#  Pelaajatilastot


@app.route('/stats')
def stats():
    players = Player.query.order_by(Player.points.desc()).all()
    return render_template('stats.html', players=players)

#  ADMIN EDITORI


@app.route('/editor', methods=['GET', 'POST'])
def editor():
    if 'admin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('action')

        # 🔹 Pelaajien muokkaus
        if action == "add":
            new_player = Player(
                firstname=request.form.get('firstname', ''),
                lastname=request.form.get('lastname', ''),
                games_played=int(request.form.get('games_played', 0)),
                goals=int(request.form.get('goals', 0)),
                assists=int(request.form.get('assists', 0)),
                penalty_minutes=int(request.form.get('penalty_minutes', 0))
            )
            db.session.add(new_player)

        elif action == "update" and request.form.get('player_id'):
            player = Player.query.get(int(request.form.get('player_id')))
            if player:
                player.games_played = int(request.form.get(
                    'games_played', player.games_played))
                player.goals = int(request.form.get('goals', player.goals))
                player.assists = int(
                    request.form.get('assists', player.assists))
                player.penalty_minutes = int(request.form.get(
                    'penalty_minutes', player.penalty_minutes))

        elif action == "delete" and request.form.get('player_id'):
            player = Player.query.get(int(request.form.get('player_id')))
            if player:
                db.session.delete(player)

        # 🔹 Kokoonpanon muokkaus (pelaajakohtaiset kentät)
        elif action == "update_lineup":
            lineup = Lineup.query.first()
            if not lineup:
                lineup = Lineup()

            # Päivitetään hyökkäysketjut
            lineup.attack1_player1 = request.form.get('attack1_player1', '')
            lineup.attack1_player2 = request.form.get('attack1_player2', '')
            lineup.attack1_player3 = request.form.get('attack1_player3', '')

            lineup.attack2_player1 = request.form.get('attack2_player1', '')
            lineup.attack2_player2 = request.form.get('attack2_player2', '')
            lineup.attack2_player3 = request.form.get('attack2_player3', '')

            lineup.attack3_player1 = request.form.get('attack3_player1', '')
            lineup.attack3_player2 = request.form.get('attack3_player2', '')
            lineup.attack3_player3 = request.form.get('attack3_player3', '')

            # Päivitetään puolustajaparit
            lineup.defense1_player1 = request.form.get('defense1_player1', '')
            lineup.defense1_player2 = request.form.get('defense1_player2', '')

            lineup.defense2_player1 = request.form.get('defense2_player1', '')
            lineup.defense2_player2 = request.form.get('defense2_player2', '')

            lineup.defense3_player1 = request.form.get('defense3_player1', '')
            lineup.defense3_player2 = request.form.get('defense3_player2', '')

            # Päivitetään maalivahti
            lineup.goalie = request.form.get('goalie', '')

            db.session.add(lineup)

        try:
            db.session.commit()
        except Exception as e:
            print(f"Database commit failed: {e}")
            db.session.rollback()

        return redirect(url_for('editor'))

    players = Player.query.order_by(Player.points.desc()).all()
    lineup = get_lineup()
    return render_template('editor.html', players=players, lineup=lineup)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            # Ohjaa editoriin onnistuneen kirjautumisen jälkeen
            return redirect(url_for('editor'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))


# ℹ️ Lisätietoja joukkueesta


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/healthz')
def health_check():
    return "OK", 200


with app.app_context():
    db.create_all()
    print("✅ Tietokanta ja taulut luotu (tai olemassa jo).")

if __name__ == '__main__':
    app.run(debug=True)
