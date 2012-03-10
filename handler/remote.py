from MythTV import MythDB, MythBE, Frontend, MythVideo, MythXML, MythLog, MythError, Video
from flask import Blueprint, render_template, abort, request
from model.utils import FEConnect, mythtv_frontends

remote = Blueprint('remote', __name__)

@remote.route('/')
def index():
    """
    Remote controller index
    """
    return render_template('remote.html')


@remote.route('/<host>', methods = ['POST'])
def keyboard(host):
    """
    Handels the sending of the events to the frontend
    """
    if FEConnect(host) and 'key' in request.form:
        key = request.form['key']
        if key.startswith('jumpto:'):
            mythtv_frontends[host].jump[key[7:]]
        else:
            mythtv_frontends[host].key[key]
    else:
        return '', 500
    return ''
