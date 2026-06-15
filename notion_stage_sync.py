#!/usr/bin/env python3
"""Adstr Stage Sync — Route 3 (Notion API automation)."""

import os, re, sys, time, requests

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
HEADERS = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
API = "https://api.notion.com/v1"

DB_MASTER  = "37044225-6652-8133-84e3-e044fbf22942"
DB_FLOW    = "37044225-6652-8188-8496-c3945046d0ea"
DB_TRACKER = "06a44225-6652-83ac-94d2-015afef1b629"
DB_CONCEPT = "f6a176a3-e058-4c94-8d39-8c42d5b9a41c"

M_CONCEPT_NO="Concept No. "; M_CONCEPT_NM="Concept Name"; M_ROUND="Official Round"
M_TYPE="Type"; M_PRODUCT="Product"; M_CLIENT_REL="Current Clients"; M_CREATOR="Creator(s)"
M_CS_STATUS="CS Status"; M_STAGE="🎯 Stage"

F_JOBNAME="Job#_Name"; F_ROUND="Offical Round"; F_CLIENT="Client"
F_FORMAT="Format"; F_STATUS="Status"; F_SCRIPT="Script Link"; F_REVIEW="Review Link"

T_CLIENT="Client"; T_ROUND="Round "; T_NOTES="📝 Notes"; T_COMPLETION="🏁 Round Completion"; T_HEALTH="🚦 Round Health"

C_CONCEPT="Concept"; C_CLIENT="Client"; C_ROUND="Round"; C_NUM="Concept #"; C_SKU="SKU"
C_CREATOR="Creator"; C_STAGE="🎯 Stage"; C_EDIT="✂️ Editing Status"
C_FORMAT="Format"; C_SCRIPT="Script Link"; C_REVIEW="Review Link"
C_LINK="🔗 Concept"; C_BRAND="Clients"

CLIENT_IDS = {
    "Ninja":"85a5b1ef-6e78-44cf-a71e-64e1b386f710","Tao Clean":"34944225-6652-80b6-9634-d79aa269f786",
    "Nu Harvest":"34444225-6652-8073-949a-dc06806668a3","SoleBrace":"31844225-6652-80d2-bfb0-cffc7e820f48",
    "Frase Skin":"1e844225-6652-80dc-8fa6-cba66e6d7623","PuraU":"2a644225-6652-80f3-9076-c86a7f2ca51d",
    "Whif":"2f044225-6652-8070-abcb-ef1cc92f1de3","Hyro":"2f144225-6652-808e-b2f7-d3d5f0b772c5",
    "Healr":"21444225-6652-8000-b9c8-d60778236d25",
}

CLIENT_MAP = [
    ("Ninja FS605 SLUSHi MAX",        "Round 22",  "Ninja",      "FS605 Slushi Max", "Ninja",     "🥷 Ninja"),
    ("Ninja FS302 PKANZ SLUSHi Pink", "Round 22",  "Ninja",      "FS302",            "Ninja",     "🥷 Ninja"),
    ("Ninja FN101PKANZ CRISPi Pink",  "Round 22",  "Ninja",      "FN101",            "Ninja",     "🥷 Ninja"),
    ("Ninja NC302 CREAMi Pink",       "Round 22",  "Ninja",      "NC302",            "Ninja",     "🥷 Ninja"),
    ("Ninja AS101 CRISPi Pro",        "Round 23",  "Ninja",      "AS101",            "Ninja",     "🥷 Ninja"),
    ("Ninja DB351 BlendBOSS",         "Round 23",  "Ninja",      "DB351",            "Ninja",     "🥷 Ninja"),
    ("Ninja ES601 Luxe Cafe",         "Round 23",  "Ninja",      "ES601",            "Ninja",     "🥷 Ninja"),
    ("Ninja NC501 Creami",            "Round 23",  "Ninja",      "NC501",            "Ninja",     "🥷 Ninja"),
    ("Ninja NC300 CREAMi",            "Round 24",  "Ninja",      "NC300",            "Ninja",     "🥷 Ninja"),
    ("Tao Clean",                     "Round 1",   "Tao Clean",  None,               "Tao Clean", "🦷 Tao Clean"),
    ("Tao Clean",                     "Round 2",   "Tao Clean",  None,               "Tao Clean", "🦷 Tao Clean"),
    ("Nu Harvest",                    "Round 1",   "Nu Harvest", None,               "Nu Harvest","🎀 Nu Harvest"),
    ("SoleBrace",                     "Round 2",   "SoleBrace",  None,               "SoleBrace", "🦶 SoleBrace"),
    ("Frase Skin",                    "Round 10",  "Frase Skin", None,               "Frase Skin","👷 Frase Skin"),
    ("PuraU",                         "Round 4",   "PuraU",      None,               "PuraU",     "💊 PuraU"),
    ("PuraU",                         "Round 5",   "PuraU",      None,               "PuraU",     "💊 PuraU"),
    ("Whif",                          "Round 4",   "Whif",       None,               "WHIF",      "👃 Whif"),
    ("Whif",                          "Round 5",   "Whif",       None,               "WHIF",      "👃 Whif"),
    ("Hyro",                          "Round 3",   "Hyro",       None,               "Hyro",      "⚡ Hyro"),
    ("Healr",                         "Round 5",   "Healr",      None,               "Healr",     "🟠 Healr"),
]

CS_TO_STAGE = {"Reached Out [WhatsApp]":"🔒 Locking in creator","Reached Out [Email]":"🔒 Locking in creator",
"In Talks - Keen":"🔒 Locking in creator","Signing Contract":"🔒 Locking in creator","Agreed":"🔒 Locking in creator",
"Ordered Product":"📦 Product sent","Filming":"🎬 Filming","REVISIONS":"🔄 Creator revisions",
"Reviewing":"🎞️ In editing","FLOW":"🎞️ In editing","COMPLETE":"🏁 Exported"}
FLOW_TO_STAGE = {"Update Status":"🎞️ In editing","Awaiting Assets":"🎞️ In editing","Ready to Edit":"🎞️ In editing",
"In Editing":"🎞️ In editing","Internal Review":"🎞️ In editing","Ready For Review":"🎞️ In editing",
"Notes given":"✂️ Editing revisions","Revisions":"✂️ Editing revisions","Revisions Amended":"✂️ Editing revisions",
"Need End Cards":"✂️ Editing revisions","Need 4x5 version":"✂️ Editing revisions","Pending Approval":"✅ Approved internally",
"4x5s Approved":"✅ Approved internally","Client Review":"✅ Approved internally","Pending Export":"📤 Pending export",
"Pending Exports":"📤 Pending export","Exported":"🏁 Exported"}
FLOW_TO_EDIT = {"Ready to Edit":"Ready to Edit","Update Status":"Ready to Edit","Awaiting Assets":"Ready to Edit",
"In Editing":"In Editing","Internal Review":"In Editing","Ready For Review":"Ready for Review","Notes given":"Revisions",
"Revisions":"Revisions","Revisions Amended":"Revisions","Need End Cards":"Revisions","Need 4x5 version":"Revisions",
"Client Review":"Client Review","Pending Approval":"Client Review","4x5s Approved":"Client Review",
"Pending Export":"Pending Export","Pending Exports":"Pending Export","Exported":"Exported"}
EMOJI = {"🔒 Locking in creator":"🔒","📦 Product sent":"📦","🎬 Filming":"🎬","🔄 Creator revisions":"🔄",
"🎞️ In editing":"🎞️","✂️ Editing revisions":"✂️","✅ Approved internally":"✅","📤 Pending export":"📤","🏁 Exported":"🏁"}
SEP = "———————"

def _post(p,b): r=requests.post(f"{API}{p}",headers=HEADERS,json=b,timeout=30); r.raise_for_status(); return r.json()
def _patch(p,b): r=requests.patch(f"{API}{p}",headers=HEADERS,json=b,timeout=30); r.raise_for_status(); return r.json()

def query_db(db_id, filt=None):
    rows,cur=[],None
    while True:
        body={"page_size":100}
        if filt: body["filter"]=filt
        if cur:  body["start_cursor"]=cur
        d=_post(f"/databases/{db_id}/query",body); rows+=d["results"]
        if not d.get("has_more"): return rows
        cur=d["next_cursor"]; time.sleep(0.2)

def ptxt(p):
    if not p: return ""
    t=p["type"]
    if t=="title":        return "".join(x["plain_text"] for x in p["title"])
    if t=="rich_text":    return "".join(x["plain_text"] for x in p["rich_text"])
    if t=="select":       return p["select"]["name"] if p["select"] else ""
    if t=="status":       return p["status"]["name"] if p["status"] else ""
    if t=="multi_select": return ",".join(o["name"] for o in p["multi_select"])
    if t=="url":          return p.get("url") or ""
    return ""

def first_rel_id(p):
    if p and p.get("type")=="relation" and p.get("relation"):
        return p["relation"][0]["id"]
    return ""

def cnum_job(s):
    m=re.search(r"C(\d+)",s or "",re.IGNORECASE); return int(m.group(1)) if m else None
def cnum_master(s):
    m=re.search(r"(\d+)",s or ""); return int(m.group(1)) if m else None

def records_for(client_id, product, round_name, flow_client):
    flt={"and":[{"property":M_ROUND,"select":{"equals":round_name}}]}
    if client_id:
        flt["and"].append({"property":M_CLIENT_REL,"relation":{"contains":client_id}})
    master=query_db(DB_MASTER, flt)
    concepts={}
    for row in master:
        pr=row["properties"]
        if product and product.lower() not in ptxt(pr.get(M_PRODUCT)).lower(): continue
        n=cnum_master(ptxt(pr.get(M_CONCEPT_NO)))
        if n is None: continue
        concepts[n]={"cs":ptxt(pr.get(M_CS_STATUS)),"type":ptxt(pr.get(M_TYPE)),
                     "name":ptxt(pr.get(M_CONCEPT_NM)) or ptxt(pr.get(M_CONCEPT_NO)),
                     "creator_id":first_rel_id(pr.get(M_CREATOR)),"product":ptxt(pr.get(M_PRODUCT)),"pid":row["id"]}
    paid=[]
    for n in sorted(concepts):
        if concepts[n]["type"].strip().upper().startswith("UGC"): paid.append(n)
        elif "STATIC" in concepts[n]["type"].upper(): break
    paid=set(paid)
    flow={}
    try:
        for row in query_db(DB_FLOW, {"and":[{"property":F_ROUND,"select":{"equals":round_name}},
                                             {"property":F_CLIENT,"select":{"equals":flow_client}}]}):
            pr=row["properties"]
            if "video" not in ptxt(pr.get(F_FORMAT)).lower(): continue
            n=cnum_job(ptxt(pr.get(F_JOBNAME)))
            if n is not None:
                flow[n]={"status":ptxt(pr.get(F_STATUS)),"script":ptxt(pr.get(F_SCRIPT)),"review":ptxt(pr.get(F_REVIEW))}
    except requests.HTTPError: pass
    out={}
    for n in sorted(paid):
        cs=concepts[n]["cs"]; f=flow.get(n,{}); fs=f.get("status")
        if fs and fs in FLOW_TO_STAGE: stage=FLOW_TO_STAGE[fs]
        elif cs in CS_TO_STAGE:        stage=CS_TO_STAGE[cs]
        elif cs=="Failed":             stage="❌ Failed"
        else:                          stage="⚪ no status yet"
        out[n]={"name":concepts[n]["name"],"creator_id":concepts[n]["creator_id"],"product":concepts[n]["product"],
                "stage":stage,"edit":FLOW_TO_EDIT.get(fs,""),"script":f.get("script",""),"review":f.get("review",""),"pid":concepts[n]["pid"]}
    return out

def set_master_stage(pid, stage):
    if stage.startswith(("⚪","❌")): return
    _patch(f"/pages/{pid}", {"properties":{M_STAGE:{"select":{"name":stage}}}})

def upsert_concept(client_lbl, round_name, n, rec, sku="", brand_id=""):
    title=rec["name"] or f"{client_lbl} {round_name} C{n}"
    sku=(sku or "").split(",")[0].strip()   # one product name for the SKU select
    props={C_CONCEPT:{"title":[{"type":"text","text":{"content":f"C{n} — {title}"}}]},
        C_CLIENT:{"select":{"name":client_lbl}},C_ROUND:{"select":{"name":round_name}},
        C_NUM:{"select":{"name":f"Concept {n}"}},C_FORMAT:{"select":{"name":"UGC"}},
        C_LINK:{"relation":[{"id":rec["pid"]}]}}
    if sku: props[C_SKU]={"select":{"name":sku}}
    if brand_id: props[C_BRAND]={"relation":[{"id":brand_id}]}
    if rec.get("creator_id"): props[C_CREATOR]={"relation":[{"id":rec["creator_id"]}]}
    if not rec["stage"].startswith(("⚪","❌")): props[C_STAGE]={"select":{"name":rec["stage"]}}
    if rec["edit"]:   props[C_EDIT]={"select":{"name":rec["edit"]}}
    if rec["script"]: props[C_SCRIPT]={"url":rec["script"]}
    if rec["review"]: props[C_REVIEW]={"url":rec["review"]}
    keyflt=[{"property":C_CLIENT,"select":{"equals":client_lbl}},{"property":C_ROUND,"select":{"equals":round_name}},
            {"property":C_NUM,"select":{"equals":f"Concept {n}"}},
            {"property":C_SKU,"select":{"equals":sku}} if sku else {"property":C_SKU,"select":{"is_empty":True}}]
    found=query_db(DB_CONCEPT, {"and":keyflt})
    if found: _patch(f"/pages/{found[0]['id']}", {"properties":props})
    else:     _post("/pages", {"parent":{"database_id":DB_CONCEPT},"properties":props})

def update_tracker(pid, recs, existing):
    lines=["📋 Concept status (auto-synced)"]; exported=0; stages=[]
    for n in sorted(recs):
        st=recs[n]["stage"]; stages.append(st); emo=EMOJI.get(st,"•"); word=st.split(" ",1)[1] if " " in st else st
        lines.append(f"C{n}: {emo} {word}")
        if st=="🏁 Exported": exported+=1
    total=len(recs); pct=round(100*exported/total) if total else 0
    if total and exported==total: health="✅ Round complete"
    elif any(s in ("🔄 Creator revisions","✂️ Editing revisions") for s in stages): health="🔴 Roadblock"
    elif pct>=60: health="🟢 Nearly there"
    elif pct>=20 or any(s in ("🎬 Filming","🎞️ In editing","✅ Approved internally","📤 Pending export") for s in stages): health="🟡 In progress"
    else: health="🟠 Just getting started"
    human=existing.split(SEP,1)[1].strip() if SEP in existing else existing.strip()
    notes=("\n".join(lines)+f"\n{SEP}\n"+human)[:1900]
    _patch(f"/pages/{pid}", {"properties":{T_NOTES:{"rich_text":[{"type":"text","text":{"content":notes}}]},
        T_COMPLETION:{"rich_text":[{"type":"text","text":{"content":f"{exported}/{total} exported ({pct}%)"}}]},
        T_HEALTH:{"select":{"name":health}}}})

def tracker_page(client, round_name):
    rows=query_db(DB_TRACKER, {"and":[{"property":T_CLIENT,"title":{"equals":client}},
                                      {"property":T_ROUND,"status":{"equals":round_name}}]})
    return rows[0] if rows else None

def main():
    if not NOTION_TOKEN: sys.exit("Set NOTION_TOKEN first.")
    for client,round_name,brand,product,flow_client,lbl in CLIENT_MAP:
        try:
            recs=records_for(CLIENT_IDS.get(brand,""),product,round_name,flow_client)
            if not recs:
                print(f"WARN  {client} {round_name}: no concepts found"); continue
            for n,rec in recs.items():
                set_master_stage(rec["pid"],rec["stage"])
                upsert_concept(lbl,round_name,n,rec,sku=rec["product"],brand_id=CLIENT_IDS.get(brand,""))
            page=tracker_page(client,round_name)
            if page: update_tracker(page["id"],recs,ptxt(page["properties"].get(T_NOTES)))
            print(f"OK  {client} {round_name}: {len(recs)} concepts")
        except Exception as e:
            print(f"ERROR  {client} {round_name}: {e}")

if __name__=="__main__":
    main()
