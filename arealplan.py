#!/usr/bin/env python
import time
import requests
from feedgen.feed import FeedGenerator
from yaml import load, dump
from datetime import datetime
import pytz

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def get_arealplan_json():
    r = requests.get("https://www.bergen.kommune.no/publisering/api/kunngjoringer/liste/?bydel=alle_bydeler&status=arealplan&tekst=&fra=0&antall=50&_="+str(int(time.time())))
    return r.json()

def get_cache():
    rawcache = ""
    try:
        rawcache = open("arealplan.yaml").read()
    except:
        print("No cached items");
        return {"items":[]}
    return load(rawcache, Loader=Loader)

def save_cache(cache):
    with open("arealplan.yaml", "w") as out:
        out.write(dump(cache, Dumper=Dumper))

cache = get_cache()

cached_ids = [e["id"] for e in cache["items"]]

fg = FeedGenerator()
fg.id("https://elzapp.com/feeds/bk_arealplan.xml")
fg.title("Bergen Kommune Arealplaner")
fg.author({"name": "Elzapp", "email": "elzapp@elzapp.com"})
fg.language("no")
new = [e for e in get_arealplan_json()["kunngjoringer"] if e["id"] not in cached_ids]
for treff in new:
    treff["seen"] = datetime.utcnow()
    cache["items"].append(treff)
for treff in sorted(cache["items"],key=lambda x: x["seen"].isoformat()):
    fe = fg.add_entry()
    fe.updated(pytz.utc.localize(treff["seen"]))
    fe.id(treff["id"])
    fe.title(treff["navn"])
    fe.description(treff["ingress"])
    fe.link(href="https://www.bergen.kommune.no"+treff["url"])
    #print(treff)
save_cache(cache)
#print(fg.atom_str(pretty=True).decode("UTF-8"))
fg.atom_file("bk_arealplan.xml", pretty=True)
