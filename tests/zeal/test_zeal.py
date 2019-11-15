from zeal import zeal


def test_list_installed_docsets():
    docsets = zeal.list_installed_docsets("tests/data/docsets")
    assert len(docsets) == 2
    py_dcs = [d for d in docsets if "Python" in d["title"]][0]
    assert "python" in py_dcs["keywords"]
    assert "python3" in py_dcs["keywords"]
    assert "icon" in py_dcs
    lua_dcs = [d for d in docsets if "Lua" in d["title"]][0]
    assert "lua" in lua_dcs["keywords"]
    assert "icon" not in lua_dcs


def test_fuzzy_keyword_filter_broad():
    kws = zeal.fuzzy_filter_keywords(["py", "lua", "kpt"], "p")
    best_match = kws[0]
    assert best_match == "py"
    assert "kpt" in kws
    assert "lua" not in kws


def test_fuzzy_keyword_filter_concrete():
    kws = zeal.fuzzy_filter_keywords(["py", "lua", "kpt"], "py")
    assert "py" in kws
    assert len(kws) == 1


def test_fuzzy_keyword_filter_mismatch():
    kws = zeal.fuzzy_filter_keywords(["py", "lua", "kpt"], "dd")
    assert len(kws) == 0
