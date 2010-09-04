autocastr
========
*what?*  
Download your podcasts and separate them into CD-R sized folders to allow for quick burning

*why?*  
Because I'm cheap -- now you can listen to podcasts in your car without aftermarket sound systems or crappy
mp3 player docks, just use your CD player!

*how?*  
Get the source:

    git clone git://github.com/swanson/autocastr.git

Add the RSS feeds for the podcasts you want (only supports MP3s) to `feeds.txt`

Run the script to check for download new podcasts (make a cron job if you are a cool):

    cd autocastr
    python autocastr.py

*where?*  
After you run the script, your podcasts are the `autocastr/podcasts/` directory, split into folders that you can easily burn to a CD with your favorite program.

*how can i..?*  

  - add feeds?  add them to `feeds.txt`
  - remove feeds? remove them from `feeds.txt`
  - increase the backlog size? change `max_backlog` in `settings.config`
  - increase the folder size limit? change `folder_size` in `settings.config`
  - do something weird that you didn't list here? fork the project and add it yourself buddy!
