from MythTV import MythXML
from flask import Blueprint, render_template
from model.utils import mythDB

settings = Blueprint('settings', __name__)

mythXML = MythXML(db = mythDB)

@settings.route('/')
def index():
    return render_template('settings.html', frontends = mythXML.getHosts())