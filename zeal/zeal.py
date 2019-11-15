"""
Interact with Zeal app:
- Parse docset info
- Pass search queries to it
"""
import os
import json
import plistlib
import subprocess
from operator import itemgetter
import logging
from . import wmctrl

LOGGER = logging.getLogger(__name__)


def get_nested(data, *args):
    """
    Retrieve values inside nested dicts
    """
    if args and data:
        element = args[0]
        if element:
            value = data.get(element)
            return value if len(args) == 1 else get_nested(value, *args[1:])
    return None


def list_installed_docsets(path):
    """
    Find all installed Zeal docsets
    """
    path = os.path.expanduser(path)
    docsets = []
    for dirname in os.listdir(path):
        if dirname.endswith(".docset"):
            docset_path = os.path.join(path, dirname)
            meta_file = os.path.join(docset_path, "meta.json")
            icon_file = os.path.join(docset_path, "icon@2x.png")
            if os.path.exists(meta_file):
                with open(meta_file) as f:
                    try:
                        meta = json.load(f)
                        kws = get_nested(meta, "extra", "keywords")
                        if not kws:
                            kws = get_docset_kw_from_plist(docset_path) or [
                                meta["title"].replace(" ", "").lower()
                            ]
                        docset = {"title": meta["title"], "keywords": kws}
                        if os.path.exists(icon_file):
                            docset["icon"] = icon_file
                        docsets.append(docset)
                    except Exception as exc:  # pylint: disable=broad-except
                        LOGGER.error(exc)
    return docsets


def get_docset_kw_from_plist(docset_path):
    """
    Get Zeal keyword from a Zeal docset plist file
    """
    plist_file = os.path.join(docset_path, "Contents", "Info.plist")
    if os.path.exists(plist_file):
        with open(plist_file, "rb") as f:
            plist = plistlib.load(f)
            return [plist["CFBundleIdentifier"]]
    return []


def query_docset(keyword, query):
    """
    Pass search query to Zeal
    """
    try:
        subprocess.run(["zeal", f"{keyword}:{query}"], check=False)
    except FileNotFoundError:
        LOGGER.error("can't execute 'zeal' - is Zeal installed?")
        return

    try:
        wmctrl.activate_window_by_class_name("zeal.Zeal")
    except wmctrl.WmctrlNotFoundError:
        LOGGER.warning("wmctrl not installed, unable to activate Zeal app window")


def fuzzy_filter_keywords(docset_keywords, query_keyword):
    """
    Match strings fuzzily
    """
    # step 1: keywords must contain every char in query
    qchars = set(query_keyword.lower())
    keywords = [
        kw for kw in docset_keywords if len(set(kw.lower()) & qchars) == len(qchars)
    ]

    # step 2: chars must be in the same order
    kws = []
    for keyword in keywords:
        idx_chars = [(i, c) for (i, c) in enumerate(keyword.lower()) if c in qchars]
        kw_filtered = "".join(ic[1] for ic in idx_chars)
        sq_idx_sum = sum(ic[0] ** 2 for ic in idx_chars)

        if kw_filtered == query_keyword.lower():
            kws.append((keyword, sq_idx_sum))

    # step 3: sort by the squared char index sum
    kws = sorted(kws, key=itemgetter(1))
    return [i[0] for i in kws]
