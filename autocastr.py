# Download your podcasts and separate them into CD-R sized folders to allow for quick burning

# *why?* 
# Because I'm cheap -- now you can listen to podcasts in your car without aftermarket 
# sound systems or crappy mp3 player docks, just use your CD player!
# ---


# External dependancy, too lazy to parse
# RSS feeds myself
try:
    import feedparser
except:
    raise Exception("You need feedparser! Use pip or easy_install to get it")

import os, shutil, re, urllib2, json, time, glob, sys

# Settings are stored in an external JSON
# file
with open('settings.json', 'r') as fp:
    settings = json.loads(fp.read())

# Threshold for making a new folder
DIR_LIMIT = settings['folder_size'] * 1048576

# How many old episodes per feed to retrieve
MAX_BACKLOG = settings['max_backlog']
FOLDER_FORMAT = os.path.join('podcasts','cd-%s')
AUDIO_MIME = re.compile('audio/.*', re.I)

# Use a list comprehension to generate a list
# of feed URLs
tracked_feeds = settings['feeds']
tracked_urls = [f['url'] for f in tracked_feeds]

# The feeds we want to track are stored in a
# text file
with open('feeds.txt', 'r') as fp:
    feeds = fp.read()

feeds = feeds.strip().split('\n')

# Add any new feeds to settings
for feed in feeds:
    if feed not in tracked_urls:
        settings['feeds'].append({'url':feed, 'last_checked':0})

# Remove any feeds that we don't want to download anymore,
# notice that I make a copy of the list so I can operate
# on it while in the loop context
for i, existing in enumerate(settings['feeds'][:]):
    if existing['url'] not in feeds:
        settings['feeds'].pop(i)

# Return the latest folder in the podcasts directory, based on the highest number
def get_latest_folder():
    glob_path = FOLDER_FORMAT % '*'
    cds = glob.glob(glob_path)
    # Do some python-fu to get the max directory number
    latest = max([int(re.sub('[^\d]', '', c)) for c in cds])
    return latest

# Helper to clear out all old podcasts
def clean_root():
    # Who needs recursive directory walking when you have shutil!
    shutil.rmtree('podcasts', True)
    os.mkdir('podcasts')

# Strips filename of any strange characters so the 
# OS won't complain when we try to save it
def clean_filename(value):
    # Bad but w/e
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)


# Writes the mp3 to the first available directory; if adding 
# it to the lastest directory will cause the folder
# to exceed the size limit then a new folder is created and 
# the file is stored there
def add_file(data, name, filesize):
    name = clean_filename(name)
    latest_dir = FOLDER_FORMAT % get_latest_folder()
    size = sum([os.path.getsize(os.path.join(latest_dir, f)) for f in os.listdir(latest_dir)])
    if size + filesize > DIR_LIMIT:
        latest_dir = FOLDER_FORMAT % (get_latest_folder() + 1)
        os.mkdir(latest_dir)
    with open(os.path.join(latest_dir, name) + '.mp3', 'wb') as fp:
        fp.write(data) 

default_path = FOLDER_FORMAT % '0'
# Make sure the folder exists on disk, if it doesn't create it
if not os.path.exists(default_path):
    os.mkdir(default_path)

# Loop over the feeds
for feed in settings['feeds']:
    d = feedparser.parse(feed['url'])
    print 'Checking for new episodes of', d['feed']['title']
    ep_count = 0

    # __some__ podcast feeds are dumb and don't put the newest episodes at the top...
    # lambda to the rescue
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
    # Make the time of the latest entry so we don't bother checking stuff multiple times
    feed['last_checked'] = time.mktime(max([e['updated_parsed'] for e in d['entries']]))
    
    # I don't know why this was in the loop, probably doesn't need to be
    with open('settings.json', 'w') as fp:
        json.dump(settings, fp, indent = 4)

print 'Done.'
sys.exit()

