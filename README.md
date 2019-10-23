# Selenium scraping bot #
The bot for scraping site contents by script based on selenium module. 
Supported browsers: google chrome, firefox, opera, phantomjs
Supported virtual display for non-graphical call mode 

## run sample
` python bot.py <script.xml> [params list] `

## install components
**selemium** `sudo pip install selenium`
**lxml** `sudo pip install lxml`
**virtual display** `sudo apt-get install xvfb` `sudo pip install pyvirtualdisplay`
**chromedriver** version not less than 2.31! from `https://sites.google.com/a/chromium.org/chromedriver/downloads` install to `/usr/local/bin`

## xml script tags:

**bot** - root tag

**site** - scan site params

**base** - set base marker for further use '.' in xpath

**foreach** - cycle for group operation with list of the elements

**if** - condition for execute or pass subtags

**nav** - navigation action (change page / or page options)

**collect** - collect data from site to common plane list

**col** - data column descriptor for collect tag

**params list** - optional params list

## run examples

` python bot.py tabtouch_horces.xml Beaudesert 2 `

` python bot.py tabtouch_horces.xml Beaudesert `

` python bot.py tabtouch_horces.xml `


## updates:

### sep-02-2017
  new branch: `scrap bot` (uptimization: re-use selenium from project `consel`)

### aug-25-2017
  added proxy rotation from list each selenium call 

### aug-24-2017
  added data report name style as "site-alias_time-stamp_filter1_filterN.json"
  updated proxy/chrome 

### aug-23-2017
  added site pages caching by ttl="minutes" param in script tags: site, foreach/jump

### aug-22-2017
  added proxy support
  added to script call param filters for filtration site pages that need scraping

### aug-21-2017
  first site scraping bot version
