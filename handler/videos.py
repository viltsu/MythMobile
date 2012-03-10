from MythTV import MythDB, MythBE, Frontend, MythVideo, MythXML, MythLog, MythError
from flask import Blueprint, render_template, abort, url_for, Response
from model.utils import mythDB

videos = Blueprint('videos', __name__)

mythVideo = MythVideo(db = mythDB)


@videos.route('/')
def index():
    """
    Index of the videos handler. Outputs a list of videos sorted by the title.
    """
    seen = set()
    seen_add = seen.add
    videos = []
    all_videos = mythVideo.searchVideos(insertedafter = '1900-01-01 00:00:00')

    for video in all_videos:
        path = video.filename.split('/')[0]
        if path not in seen and not seen_add(path):
            video.url = url_for('.with_path', path=path)
            video.label = path
            videos.append(video)

    videos = sorted(videos, key = lambda video: video.label.lowercase())
    return render_template('list.html', items = videos, page_title = 'Videos')


@videos.route('/<path:path>')
def with_path(path):
    """
    Show the list of videos with the given title
    """
    seen = set()
    seen_add = seen.add
    videos = []
    all_videos = list(mythVideo.searchVideos(filename = path))

    for video in all_videos:
        if video.season > 0:
            video.label = video.title + " - Season " + str(video.season)

            if video.label not in seen and not seen_add(video.label):
                video.url = "/videos/" + video.title + "/season/" + str(video.season)
                videos.append(video)

        else:
            video.label = video.title + " - " + video.subtitle
            video.url = "/videos/" + video.title + "/" + video.hash
            videos.append(video)

    if len(videos) == 1:
        videos[0].pic = url_for('.video_image', title = title, hash = videos[0].hash)
        videos[0].feplay = url_for('.video_feplay', title = title, hash = hash)
        return render_template('recording.html', item = videos[0])

    videos = sorted(videos, key = lambda video: video.season)
    return render_template('list.html', items = videos, page_title = title)


@videos.route('/<title>/season/<season>')
def with_season(title, season):
    """
    Show the videos in the given season
    """
    videos = list(mythVideo.searchVideos(title = title, season = season))

    for video in videos:
        video.label = video.title + " - " + video.subtitle
        video.url = "/videos/" + video.title + "/" + video.hash

    videos = sorted(videos, key = lambda video: video.episode)
    return render_template('list.html', items = videos, page_title = title + " Season " + str(season))


@videos.route('/<title>/<hash>')
@videos.route('/<title>/season/<season>/episode/<episode>')
def video(title, hash = None, season = None, episode = None):
    """
    Show the single video
    """
    if not hash:
        video = list(mythVideo.searchVideos(title = title, season = season, episode = episode))[0]
    else:
        video = [video for video in mythVideo.searchVideos(title = title) if video.hash == hash][0]

    return render_template('recording.html', item = video)


@videos.route('/<title>/<hash>/image.jpg')
def video_image(title, hash):
    """
    Sends the screenshot of the video
    """
    video = [video for video in mythVideo.searchVideos(title = title) if video.hash == hash][0]
    return Response(video.openScreenshot(), mimetype = 'image/png')


@videos.route('/<title>/<hash>', methods = ['POST'])
def video_feplay(title, hash):
    """
    Plays the given file in the selected frontend
    """
    return '' + title + hash