"""
Extension to query Zeal docsets
"""
from datetime import datetime, timedelta
from operator import itemgetter
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import (
    KeywordQueryEvent,
    ItemEnterEvent,
    PreferencesUpdateEvent,
)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from zeal.callable_action import callable_action, CallableEventListener
from . import zeal


MAX_DOCSETS_VISIBLE = 10


class ZealExtension(Extension):
    """ Extension class, coordinates everything """

    def __init__(self):
        super(ZealExtension, self).__init__()
        self.cached_docsets = None
        self.kw_docset_map = None
        self.active_kws = None
        self.cache_expires_at = None
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, CallableEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())

    def get_docsets_path(self):
        """
        Configurable path where Zeal docsets are installed
        """
        return self.preferences["zeal-docsets-path"]

    def process_docset_kw_arg_query(self, ukw, zkw, arg):
        """
        Process Ulauncher search query
        """
        if not self.cached_docsets:
            self.reload_docsets()
        elif self.cache_expires_at and self.cache_expires_at < datetime.now():
            self.reload_docsets()

        if zkw:
            docsets = self.list_matching_docsets(zkw)
        else:
            docsets = [
                d for (t, d) in sorted(self.cached_docsets.items(), key=itemgetter(0))
            ]

        items = []
        tail = []

        if len(docsets) > MAX_DOCSETS_VISIBLE:
            more = len(docsets) - MAX_DOCSETS_VISIBLE
            sss = "s" if more > 1 else ""
            docsets = docsets[:MAX_DOCSETS_VISIBLE]
            tail.append(
                ExtensionSmallResultItem(
                    icon="images/empty.png",
                    name=(
                        f"...{more} more docset{sss} available, "
                        "refine the query to filter..."
                    ),
                    on_enter=DoNothingAction(),
                )
            )

        for dcs in docsets:
            if arg:
                action = callable_action(zeal.query_docset, dcs["keywords"][0], arg)
            else:
                action = SetUserQueryAction("{} {} ".format(ukw, dcs["keywords"][0]))

            item = ExtensionResultItem(
                icon=dcs["icon"],
                name="{} search".format(dcs["title"]),
                description="Open Zeal and search {} documentation".format(
                    dcs["title"]
                ),
                on_enter=action,
            )
            items.append(item)
        return RenderResultListAction(items + tail)

    def list_matching_docsets(self, zkw):
        """
        Find all docsets with keywords that match `zkw`
        """
        kws = zeal.fuzzy_filter_keywords(self.active_kws, zkw)
        dcs = []
        already_inserted = set()
        for k in kws:
            title = self.kw_docset_map[k]
            if title not in already_inserted:
                already_inserted.add(title)
                dcs.append(self.cached_docsets[title])
        return dcs

    def reload_docsets(self):
        """
        Reload information about all installed Zeal docsets
        """
        docsets = zeal.list_installed_docsets(self.get_docsets_path())
        self.cached_docsets = dict((d["title"], d) for d in docsets)
        self.kw_docset_map = dict()
        for dcs in docsets:
            for zkw in dcs["keywords"]:
                self.kw_docset_map[zkw] = dcs["title"]
        self.active_kws = set(self.kw_docset_map.keys())
        self.cache_expires_at = datetime.now() + timedelta(seconds=60)


# pylint: disable=too-few-public-methods
class KeywordQueryEventListener(EventListener):
    """ KeywordQueryEventListener class manages user input """

    def on_event(self, event, extension):
        # assuming only one ulauncher keyword: open Zeal with a query
        arg = event.get_argument()
        ukw = event.get_keyword()
        if arg:
            kw_arg = arg.split(" ", maxsplit=1)
            zkw = kw_arg[0]
            arg = kw_arg[1] if len(kw_arg) > 1 else ""
            return extension.process_docset_kw_arg_query(ukw, zkw, arg)
        return extension.process_docset_kw_arg_query(ukw, "", "")


class PreferencesUpdateEventListener(EventListener):
    """ Handle preferences updates """

    def on_event(self, event, extension):
        if event.new_value != event.old_value:
            if event.id == "zeal-docsets-path":
                extension.reload_docsets()
