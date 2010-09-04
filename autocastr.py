try:
    import feedparser
except:
    raise Exception("You need feedparser! Use pip or easy_install to get it")
import os, shutil, re, urllib2, json, time, glob, sys

with open('settings.json', 'r') as fp:
    settings = json.loads(fp.read())

DIR_LIMIT = settings['folder_size'] * 1048576
MAX_BACKLOG = settings['max_backlog']
FOLDER_FORMAT = os.path.join('podcasts','cd-%s')
AUDIO_MIME = re.compile('audio/.*', re.I)

tracked_feeds = settings['feeds']
tracked_urls = [f['url'] for f in tracked_feeds]

with open('feeds.txt', 'r') as fp:
    feeds = fp.read()

feeds = feeds.strip().split('\n')

#add any new feeds to settings
for feed in feeds:
    if feed not in tracked_urls:
        settings['feeds'].append({'url':feed, 'last_checked':0})

#remove any feeds that we don't want to download anymore
for i, existing in enumerate(settings['feeds'][:]):
    if existing['url'] not in feeds:
        settings['feeds'].pop(i)

def get_latest_folder():
    '''
    Return the latest folder in the podcasts directory, based on the highest number
    '''
    glob_path = FOLDER_FORMAT % '*'
    cds = glob.glob(glob_path)
    latest = max([int(re.sub('[^\d]', '', c)) for c in cds])
    return latest

def clean_root():
    '''
    Helper to clear out all old podcasts
    '''
    shutil.rmtree('podcasts', True)
    os.mkdir('podcasts')

def clean_filename(value):
    '''
    Strips filename of any strange characters so the OS won't complain when we try to save it
    '''
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

def add_file(data, name, filesize):
    '''
    Writes the mp3 to the first available directory; if adding it to the lastest directory will cause the folder
    to exceed the size limit then a new folder is created and the file is stored there
    '''
    name = clean_filename(name)
    latest_dir = FOLDER_FORMAT % get_latest_folder()
    size = sum([os.path.getsize(os.path.join(latest_dir, f)) for f in os.listdir(latest_dir)])
    if size + filesize > DIR_LIMIT:
        latest_dir = FOLDER_FORMAT % (get_latest_folder() + 1)
        os.mkdir(latest_dir)
    with open(os.path.join(latest_dir, name) + '.mp3', 'wb') as fp:
        fp.write(data) 

default_path = FOLDER_FORMAT % '0'
if not os.path.exists(default_path):
    os.mkdir(default_path)

for feed in settings['feeds']:
    d = feedparser.parse(feed['url'])
    print 'Checking for new episodes of', d['feed']['title']
    ep_count = 0

    #some podcast feeds are dumb and not put the newest episodes at the top...
    sorted_entries = sorted(d['entries'], cmp = lambda x,y: cmp(y['updated_parsed'], x['updated_parsed']))
    for episode in sorted_entries:
        if ep_count >= MAX_BACKLOG:
            break
        if time.mktime(episode['updated_parsed']) <= feed['last_checked']:
            continue
        if 'enclosures' in episode:
            type = episode['enclosures'][0].type
            if AUDIO_MIME.search(type) is not None:
                print 'Downloading %s - %s\n' % (episode['title'], episode['enclosures'][0].href)
                file = urllib2.urlopen(episode['enclosures'][0].href)
                filename = '%s - %s' % (d['feed']['title'], episode['title'])
                filesize = int(episode['enclosures'][0].length)
                add_file(file.read(), filename, filesize)
                ep_count += 1

    feed['last_checked'] = time.mktime(max([e['updated_parsed'] for e in d['entries']]))

    with open('settings.json', 'w') as fp:
        json.dump(settings, fp, indent = 4)

print 'Done.'
sys.exit()
