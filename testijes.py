from app import db, Player
players = Player.query.all()

for p in players:
    print(f"{p.firstname} {p.lastname} - Ottelut: {p.games_played}, Maalit: {p.goals}, Syötöt: {p.assists}")
