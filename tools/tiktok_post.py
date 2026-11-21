"""Wisselt de TikTok-code in voor een token en post een video (Content Posting API, Direct Post).
Sleutels komen uit GitHub Secrets; er wordt nooit een token of sleutel gelogd."""
import os, sys, json, time, requests
B = "https://open.tiktokapis.com/v2"
code, video, title = os.environ["CODE"], os.environ.get("VIDEO", "media/demo-short.mp4"), os.environ.get("TITLE", "Islam for the Curious")
r = requests.post(f"{B}/oauth/token/", data={"client_key": os.environ["CK"], "client_secret": os.environ["CS"], "code": code,
                  "grant_type": "authorization_code", "redirect_uri": "https://ahmed-132.github.io/iftc/"},
                  headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=60).json()
if "access_token" not in r: sys.exit(f"Token mislukt: {r.get('error')} {r.get('error_description')}")
tok = r["access_token"]; print("::add-mask::" + tok); H = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8"}
info = requests.post(f"{B}/post/publish/creator_info/query/", headers=H, timeout=60).json()
opts = info.get("data", {}).get("privacy_level_options", [])
print("Account:", info.get("data", {}).get("creator_username"), "| privacy-opties:", opts)
privacy = "SELF_ONLY" if "SELF_ONLY" in opts or not opts else opts[0]
size = os.path.getsize(video)
init = requests.post(f"{B}/post/publish/video/init/", headers=H, timeout=60, data=json.dumps({
    "post_info": {"title": title, "privacy_level": privacy, "disable_comment": False, "disable_duet": False, "disable_stitch": False},
    "source_info": {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size, "total_chunk_count": 1}})).json()
if init.get("error", {}).get("code") not in (None, "ok"): sys.exit(f"Init mislukt: {init['error']}")
d = init["data"]
up = requests.put(d["upload_url"], data=open(video, "rb").read(), timeout=600,
                  headers={"Content-Type": "video/mp4", "Content-Range": f"bytes 0-{size - 1}/{size}", "Content-Length": str(size)})
print("Upload:", up.status_code)
for _ in range(30):
    s = requests.post(f"{B}/post/publish/status/fetch/", headers=H, timeout=60, data=json.dumps({"publish_id": d["publish_id"]})).json()
    st = s.get("data", {}).get("status"); print("Status:", st)
    if st in ("PUBLISH_COMPLETE", "FAILED"): break
    time.sleep(10)
if st != "PUBLISH_COMPLETE": sys.exit(f"Niet gelukt: {s}")
print("GEPOST met zichtbaarheid", privacy)
