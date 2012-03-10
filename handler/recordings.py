from MythTV import MythDB, MythBE, Frontend, MythVideo, MythXML, MythLog, MythError
from flask import Blueprint, render_template, abort, Response, request, url_for
from model.utils import mythDB, mythtv_frontends, FEConnect

recordings = Blueprint('recordings', __name__)

mythBE = MythBE(db = mythDB)
mythXML = MythXML(db = mythDB)

@recordings.route('/')
def index():
    """
    Recordigs index show an alphabetical list of all the recordings
    much in the same way as the backend
    """
    all_recordins = [recording for recording in mythBE.getRecordings() if recording.recgroup != 'LiveTV']
    recordings = []
    seen = set()
    seen_add = seen.add

    for recording in all_recordins:
        if recording.title not in seen and not seen_add(recording.title):
            recording.url = url_for('.with_title', title = recording.title)
            recording.label = recording.title
            recordings.append(recording)

    if not len(recordings):
        return render_template('list.html', empty = True)

    recordings = sorted(recordings, key = lambda item: item.label)
    return render_template('list.html', items = recordings, page_title = "Recordings")


@recordings.route('/<title>')
def with_title(title):
    """
    Show the recording with the given title or a list of recordings if more than one recordings with the
    same title
    """
    recordings = filter(lambda p: p.recgroup != "LiveTV" and p.title == title, mythBE.getRecordings())
    for item in recordings:
        item.label = item.title + " - " + str(item.starttime)
        item.starttime = item.starttime.strftime("%Y%m%d%H%M%S")
        item.url = url_for('.view_recording', chanid = item.chanid, starttime = item.starttime)

    if len(recordings) == 1:
        recording = recordings[0]
        recording.pic = url_for('.recording_image', chanid = recording.chanid, starttime = recording.starttime)
        recording.feplay = url_for('.programs_feplay', chanid = recording.chanid, starttime = recording.starttime)
        return render_template('recording.html', item = recordings[0])

    recordings.reverse()
    return render_template('list.html', items = recordings, page_title = title)


@recordings.route('/<chanid>/<starttime>')
def view_recording(chanid, starttime):
    """
    Show a single recording
    """
    recording = mythBE.getRecording(chanid, starttime)
    if not recording:
        return '', 404

    recording.pic = url_for('.recording_image', chanid = chanid, starttime = starttime)
    recording.feplay = url_for('.programs_feplay', chanid = chanid, starttime = starttime)
    return render_template('recording.html', item = recording)


@recordings.route('/<chanid>/<starttime>/image.jpg')
def recording_image(chanid, starttime):
    """
    Sends the preview image of the given recording
    """
    height = None
    width = None

    if 'height' in request.args:
        height = request.args['height']
    if 'width' in request.args:
        width = request.args['width']

    return Response(mythXML.getPreviewImage(chanid = int(chanid), starttime = starttime, width = width, height = height,
                                            secsin = 60),
                    mimetype = 'image/png')


@recordings.route('/<chanid>/<starttime>', methods = ['POST'])
def programs_feplay(chanid, starttime):
    """
    Plays the recording on the frontend that has been selecten.
    Frontend is send in the post data and is the value for 'frontend' key
    """
    recording = mythBE.getRecording(chanid, starttime)

    if 'frontend' in request.form:
        host = request.form['frontend']

        if FEConnect(host):
            mythtv_frontends[host].play(recording)
        else:
            return '', 500

    return ''
