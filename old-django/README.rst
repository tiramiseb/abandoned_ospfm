===========================
OSPFM, "old Django version"
===========================

After weeks of thinking, I realized that Django is clearly not the ideal framework to do what I want. That's why, before it is too late, I'm archiving this version in order to do something cleaner.

I'm planning to make :

* a "backend" server (which I made originally with Django), serving JSON data with REST requests
* some "frontend" apps (which may be dynamically served web pages, a javascript client, a heavy client, a mobile client...)

Separating the backend and the frontends make it easier to develop, focusing each part on what it really should do... So, the vast majority of Django parts will be unused on each side (no template, etc, on the backend ; no database, etc, on the frontends).
