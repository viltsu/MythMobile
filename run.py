from flask import Flask, render_template
from handler.videos import videos
from handler.recordings import recordings
from handler.remote import remote
from handler.settings import settings

app = Flask(__name__)
app.register_blueprint(videos, url_prefix='/videos')
app.register_blueprint(recordings, url_prefix='/recordings')
app.register_blueprint(remote, url_prefix='/remote')
app.register_blueprint(settings, url_prefix='/settings')

@app.route('/')
def root():
    """
    This renders the very first page
    """
    return render_template('index.html')

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5678)
