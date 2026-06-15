#!/usr/bin/env python3
"""
Adstr Stage Sync  —  Route 3 (proper Notion API automation)
"""

import os, re, sys, time, requests

# 1. CONNECTION
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
API = "https://api.notion.com/v1"

# 2. DATABASE IDs
DB_MASTER  = "37044225-6652-8133-84e3-e044fbf22942"   # Master Creative Database
DB_FLOW    = "37044225-6652-8188-8496-c3945046d0ea"   # Adstr Flow (Hub)
DB_TRACKER = "06a44225-6652-83ac-94d2-015afef1b629"   # Progress Tracker -> Clients
DB_CONCEPT = "f6a176a3-e058-4c94-8d39-8c42d5b9a41c"   # Concept Tracker

# 3. PROPERTY NAMES
M_CONCEPT_NO = "Concept No. "
M_CONCEPT_NM = "Concept Name"
M_ROUND      = "Official Round"
M_TYPE       = "Type"
M_PRODUCT    = "Product"
M_CREATOR    = "Creator(s)"
M_CS_STATUS  = "CS Status"
M_STAGE      = "🎯 Stage"

F_JOBNAME    = "Job#_Name"
F_ROUND      = "Offical Round"
F_CLIENT     = "Client"
F_FORMAT     = "Format"
F_STATUS     = "Status"
F_SCRIPT     = "Script Link"
F_REVIEW     = "Review Link"

T_CLIENT     = "Client"
T_ROUND      = "Round "
T_NOTES      = "📝 Notes"
T_COMPLETION = "🏁 Round Completion"

C_CONCEPT  = "Concept"; C_CLIENT="Client"; C_ROUND="Round"; C_NUM="Concept #"
C_CREATOR  = "Creator"; C_STAGE="🎯 Stage"; C_EDIT="✂️ Editing Status"
C_FORMAT   = "Format";  C_SCRIPT="Script Link"; C_REVIEW="Review Link"

# 4. WHICH ROWS TO SYNC
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
    ("Tao Clean",                     "Round 1",   "Tao Clean",  None
