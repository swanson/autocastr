import feedparser
import re
import os, shutil
import urllib2

DIR_LIMIT = 600 * 1048576
audio_mime = re.compile('audio/.*', re.I)

changelog_feed = "http://feeds.feedburner.com/changelogshow"
hansel_feed = "http://feeds.feedburner.com/HanselminutesCompleteMP3"

feeds = [changelog_feed, hansel_feed]

def clean_root():
    shutil.rmtree('podcasts', True)
    os.mkdir('podcasts')

def add_file(data, name):
    latest_dir = 'podcasts/cd1'
    size = os.path.getsize(latest_dir)
    if size > DIR_LIMIT:
        os.mkdir('podcast/cd2')
        latest_dir = 'podcasts/cd2'
    with open(os.path.join(latest_dir, name), 'wb') as fp:
        fp.write(data) 

clean_root()
os.mkdir('podcasts/cd1')

for feed in feeds:
    d = feedparser.parse(feed)
    print d['feed']['title']
    ep_count = 0
    for episode in d['entries']:
        if ep_count > 4:
            break
        if 'enclosures' in episode:    
            type = episode['enclosures'][0].type
            if audio_mime.search(type) is not None:
                print '%s (%s) - %s\n' % (episode['title'], episode['updated'],
                    episode['enclosures'][0].href)
                file = urllib2.urlopen(episode['enclosures'][0].href)
                add_file(file.read(), '%s - %s' %(d['feed']['title'], episode['title']))
                ep_count += 1
                
