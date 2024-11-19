from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from modules.web_application.models import ScrapedData
from modules.web_application.methods.scrapping_methods import WebScraperMethods
from flask import current_app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)
app = Flask(__name__)
db = SQLAlchemy(app)
scrape_bp = Blueprint("scrape", __name__)
scraper = WebScraperMethods()


@scrape_bp.route("/scrape", methods=["POST"])
@login_required
def scrape_url():
    data = request.json
    url = data.get("url")

    try:
        scraped_data = scraper.scrape_url(url)
        new_scrape = ScrapedData(user_id=current_user.id, url=url, **scraped_data)
        db.session.add(new_scrape)
        db.session.commit()

        return (
            jsonify(
                {"message": "Data scrapped successfully", "data": new_scrape.to_dict()}
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@scrape_bp.route("/scrapes", methods=["GET"])
@login_required
def get_user_scrapes():
    scrapes = ScrapedData.query.filter_by(user_id=current_user.id).all()
    return jsonify({"scrapes": [scrape.to_dict() for scrape in scrapes]}), 200
