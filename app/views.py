from flask import render_template

from app import app, db, cache
from app.users.models import User
from app.replays.models import Replay
from app.replays.models import ReplayPlayer
from app.replays.models import PlayerSnapshot
from app.replays.models import CombatLogMessage

from flask.ext.login import current_user

# Routes
@app.route('/')
def index():
    last_added_replays = Replay.query.order_by(Replay.added_to_site_time.desc()).limit(app.config["LATEST_REPLAYS_LIMIT"]).all()
    last_parsed_replays = Replay.query.order_by(Replay.parse_done_time.desc()).limit(app.config["LATEST_REPLAYS_LIMIT"]).all()

    # Random facts to brag about, even though they're somewhat meaningless.
    total_replays = Replay.query.count()
    total_parsed = Replay.query.filter(Replay.state == "PARSED").count()
    total_players_seen = ReplayPlayer.query.group_by(ReplayPlayer.steam_id).count()
    total_replay_snapshots = PlayerSnapshot.query.count()
    total_combat_log_entries = CombatLogMessage.query.count()

    total_users = User.query.count()
    return render_template("dotabank.html",
                           last_added_replays=last_added_replays,
                           last_parsed_replays=last_parsed_replays,
                           total_replays=total_replays,
                           total_parsed=total_parsed,
                           total_players_seen=total_players_seen,
                           total_replay_snapshots=total_replay_snapshots,
                           total_combat_log_entries=total_combat_log_entries,
                           total_users=total_users
                           )


@app.route("/privacy/")
def privacy():
    return render_template("privacy.html")


@app.route("/tos/")
def tos():
    return render_template("tos.html", emule=app.config["CONTACT_EMAIL"])


@app.route("/about/")
def about():
    return render_template("about.html", emule=app.config["CONTACT_EMAIL"])


@app.errorhandler(401)  # Unauthorized
@app.errorhandler(403)  # Forbidden
@app.errorhandler(404)  # > Missing middle!
@app.errorhandler(500)  # Internal server error.
# @app.errorhandler(Exception)  # Internal server error.
def internalerror(error):
    try:
        if error.code == 401:
            error.description = "I'm sorry Dave, I'm afraid I can't do that.  Try logging in."
        elif error.code == 403:
            if current_user.is_authenticated():
                error.description = "I'm sorry {{ current_user.name }}, I'm afraid I can't do that.  You do not have access to this resource.</p>"
            else:
                error.description = "Hacker."
    except AttributeError:
        db.session.rollback()
        error.code = 500
        error.name = "Internal Server Error"
        error.description = "Whoops! Something went wrong server-side.  Details of the problem has been sent to the Dotabank team for investigation."
    return render_template("error.html", error=error, title=error.name), error.code
