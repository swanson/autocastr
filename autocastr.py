try:
    import feedparser
except:
    raise Exception("You need feedparser! Use pip or easy_install to get it")
import os, shutil, sys, re, urllib2, json, time, glob

with open('settings.json', 'r') as fp:
    settings = json.loads(fp.read())

DIR_LIMIT = settings['folder_size'] * 1048576
MAX_BACKLOG = settings['max_backlog']
audio_mime = re.compile('audio/.*', re.I)

tracked_feeds = settings['feeds']
tracked_urls = [f['url'] for f in tracked_feeds]

with open('feeds.txt', 'r') as fp:
    feeds = fp.read()

feeds = feeds.strip().split('\n')

for feed in feeds:
    if feed not in tracked_urls:
        settings['feeds'].append({'url':feed, 'last_checked':0})

#todo: remove feeds that arent in feeds.txt from settings.json

def get_latest_folder():
    cds = glob.glob('podcasts/cd-*')
    latest = max([int(c.replace('podcasts/cd-','')) for c in cds])
    return latest

def clean_root():
    shutil.rmtree('podcasts', True)
    os.mkdir('podcasts')

def clean_filename(value):
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

def add_file(data, name):
    #todo: include size of file that will be added!
    name = clean_filename(name)
    latest_dir = 'podcasts/cd-%s' % get_latest_folder()
    size = sum([os.path.getsize(latest_dir + '/' + f) for f in os.listdir(latest_dir)])
    if size > DIR_LIMIT:
        latest_dir = 'podcasts/cd-%s' % (get_latest_folder() + 1)
        os.mkdir(latest_dir)
    with open(os.path.join(latest_dir, name), 'wb') as fp:
        fp.write(data) 

if not os.path.exists('podcasts'):
    os.mkdir('podcasts')

if not os.path.exists('podcasts/cd-0'):
    os.mkdir('podcasts/cd-0')

for feed in settings['feeds']:
    d = feedparser.parse(feed['url'])
    print 'Checking for new episodes of', d['feed']['title']
    ep_count = 0
    for episode in d['entries']:
        if ep_count >= MAX_BACKLOG:
            break
        if time.mktime(episode['updated_parsed']) <= feed['last_checked']:
            break
        if 'enclosures' in episode:    
            type = episode['enclosures'][0].type
            if audio_mime.search(type) is not None:
                print 'Downloading %s - %s\n' % (episode['title'], \
                        episode['enclosures'][0].href)
                file = urllib2.urlopen(episode['enclosures'][0].href)
                add_file(file.read(), '%s - %s' %(d['feed']['title'], episode['title']))
                ep_count += 1
    feed['last_checked'] = time.mktime(d['entries'][0]['updated_parsed'])               
    with open('settings.json', 'w') as fp:
        json.dump(settings, fp, indent = 4)
