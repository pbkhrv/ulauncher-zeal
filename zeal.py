import os
import json
import plistlib
import subprocess
from operator import itemgetter


def get_nested(data, *args):
    if args and data:
        element = args[0]
        if element:
            value = data.get(element)
            return value if len(args) == 1 else get_nested(value, *args[1:])


def list_installed_docsets(path):
    path = os.path.expanduser(path)
    docsets = []
    for d in os.listdir(path):
        if d.endswith(".docset"):
            meta_file = os.path.join(path, d, "meta.json")
            icon_file = os.path.join(path, d, "icon@2x.png")
            if os.path.exists(meta_file):
                with open(meta_file) as f:
                    try:
                        meta = json.load(f)
                        kws = get_nested(meta, "extra", "keywords")
                        if not kws:
                            kws = get_kw_from_plist(path, d)
                        docset = {"title": meta["title"], "keywords": kws}
                        if os.path.exists(icon_file):
                            docset["icon"] = icon_file
                        docsets.append(docset)
                    except Exception as e:
                        print(e)
    return docsets

def get_kw_from_plist(path, d):
    plist_file = os.path.join(path, d, "Contents", "Info.plist")
    print("getting info from " + plist_file)
    if os.path.exists(plist_file):
        with open(plist_file, 'rb') as f:
            plist = plistlib.load(f)
            return [plist["CFBundleIdentifier"]]

def query_docset(kw, query):
    subprocess.run(["zeal", "{}:{}".format(kw, query)])


def fuzzy_filter_keywords(docset_keywords, query_keyword):
    # step 1: keywords must contain every char in query
    qchars = set(query_keyword.lower())
    keywords = [
        kw for kw in docset_keywords if len(set(kw.lower()) & qchars) == len(qchars)
    ]

    # step 2: chars must be in the same order
    kws = []
    for kw in keywords:
        idx_chars = [(i, c) for (i, c) in enumerate(kw.lower()) if c in qchars]
        kw_filtered = "".join(ic[1] for ic in idx_chars)
        sq_idx_sum = sum(ic[0] ** 2 for ic in idx_chars)

        if kw_filtered == query_keyword.lower():
            kws.append((kw, sq_idx_sum))

    # step 3: sort by the squared char index sum
    kws = sorted(kws, key=itemgetter(1))
    return [i[0] for i in kws]
