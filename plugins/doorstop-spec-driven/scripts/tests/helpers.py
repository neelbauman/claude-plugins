"""テスト用モッククラスとファクトリー関数。

doorstop ライブラリへの依存を排除し、純粋な単体テストを可能にする。
"""
from __future__ import annotations

from types import SimpleNamespace


# ---------------------------------------------------------------------------
# MockLink — item.links の各要素
# ---------------------------------------------------------------------------

class MockLink:
    """doorstop Link のモック。str() で親UIDを返し、.stamp 属性を持つ。"""

    def __init__(self, uid: str, stamp=None):
        self._uid = uid
        self.stamp = stamp

    def __str__(self):
        return self._uid

    def __repr__(self):
        return f"MockLink({self._uid!r}, stamp={self.stamp!r})"


# ---------------------------------------------------------------------------
# MockItem — doorstop Item のモック
# ---------------------------------------------------------------------------

class MockItem:
    """doorstop Item のモック。

    属性アクセス (.text, .uid, .active 等) と .get()/.set() の両方をサポート。
    """

    def __init__(
        self,
        uid: str,
        text: str = "",
        header: str = "",
        level: str = "1.0",
        links: list | None = None,
        ref: str = "",
        active: bool = True,
        reviewed: bool = False,
        normative: bool = True,
        derived: bool = False,
        groups: list | None = None,
        priority: str = "medium",
        references: list | None = None,
        gherkin: str | None = None,
        test_level: str | None = None,
        stamp_value: str = "abc123",
    ):
        self.uid = _UID(uid)
        self.text = text
        self.header = header
        self.level = _Level(level)
        self.links = [
            lnk if isinstance(lnk, MockLink) else MockLink(lnk)
            for lnk in (links or [])
        ]
        self.ref = ref
        self.active = active
        self.reviewed = reviewed
        self.path = f"/fake/{uid}.yml"
        self._stamp_value = stamp_value
        self._attrs = {
            "normative": normative if not normative else None,  # None = default True
            "derived": derived,
            "groups": groups or [],
            "priority": priority,
            "references": references,
            "gherkin": gherkin,
            "test_level": test_level,
            "header": header,
        }
        # Store normative correctly
        if not normative:
            self._attrs["normative"] = False
        else:
            self._attrs["normative"] = None  # doorstop default: True

    def get(self, attr, default=None):
        if attr in self._attrs:
            return self._attrs[attr]
        return default

    def set(self, attr, value):
        self._attrs[attr] = value
        if attr == "normative":
            pass  # keep in _attrs
        elif attr == "groups":
            pass  # keep in _attrs

    def link(self, uid):
        self.links.append(MockLink(uid))

    def unlink(self, uid):
        self.links = [lnk for lnk in self.links if str(lnk) != uid]

    def clear(self, uids=None):
        """suspect 解消: 指定UIDのリンクの stamp を更新する。"""
        if uids:
            for lnk in self.links:
                if str(lnk) in uids:
                    lnk.stamp = self._stamp_value

    def review(self):
        self.reviewed = True

    def stamp(self):
        return self._stamp_value

    def save(self):
        pass  # テストではファイル書き込みしない

    def delete(self):
        pass


class _UID:
    """str() で UID 文字列を返すオブジェクト。"""
    def __init__(self, uid: str):
        self._uid = uid

    def __str__(self):
        return self._uid

    def __repr__(self):
        return self._uid

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self._uid)


class _Level:
    """str() でレベル文字列を返すオブジェクト。"""
    def __init__(self, level: str):
        self._level = level

    def __str__(self):
        return self._level

    def __repr__(self):
        return self._level


# ---------------------------------------------------------------------------
# MockDocument — doorstop Document のモック
# ---------------------------------------------------------------------------

class MockDocument:
    """doorstop Document のモック。"""

    def __init__(self, prefix: str, parent: str | None = None, items: list | None = None):
        self.prefix = prefix
        self.parent = parent or ""
        self.path = f"/fake/docs/{prefix.lower()}"
        self._items = list(items or [])

    def __iter__(self):
        return iter(self._items)

    def find_item(self, uid_str: str):
        for item in self._items:
            if str(item.uid) == uid_str and item.active:
                return item
        raise Exception(f"Item not found: {uid_str}")

    def add_item(self, **kwargs):
        uid = f"{self.prefix}{len(self._items) + 1:03d}"
        item = MockItem(uid=uid, **{k: v for k, v in kwargs.items() if k == "level"})
        self._items.append(item)
        return item

    def reorder(self, manual=False, automatic=True, keep=None):
        pass


# ---------------------------------------------------------------------------
# MockTree — doorstop Tree のモック
# ---------------------------------------------------------------------------

class MockTree:
    """doorstop Tree のモック。"""

    def __init__(self, docs: list):
        self._docs = list(docs)

    def __iter__(self):
        return iter(self._docs)

    def find_document(self, prefix: str):
        for doc in self._docs:
            if doc.prefix == prefix:
                return doc
        raise Exception(f"Document not found: {prefix}")


# ---------------------------------------------------------------------------
# ファクトリー関数
# ---------------------------------------------------------------------------

def make_link(uid: str, stamp=None) -> MockLink:
    return MockLink(uid, stamp=stamp)


def make_item(
    uid: str,
    text: str = "",
    header: str = "",
    level: str = "1.0",
    links: list | None = None,
    ref: str = "",
    active: bool = True,
    reviewed: bool = False,
    normative: bool = True,
    derived: bool = False,
    groups: list | None = None,
    priority: str = "medium",
    references: list | None = None,
    gherkin: str | None = None,
    test_level: str | None = None,
    stamp_value: str = "abc123",
) -> MockItem:
    return MockItem(
        uid=uid,
        text=text,
        header=header,
        level=level,
        links=links,
        ref=ref,
        active=active,
        reviewed=reviewed,
        normative=normative,
        derived=derived,
        groups=groups,
        priority=priority,
        references=references,
        gherkin=gherkin,
        test_level=test_level,
        stamp_value=stamp_value,
    )


def make_doc(prefix: str, parent: str | None = None, items: list | None = None) -> MockDocument:
    return MockDocument(prefix=prefix, parent=parent, items=items)


def make_tree(docs: list) -> MockTree:
    return MockTree(docs=docs)


def make_args(**kwargs) -> SimpleNamespace:
    """argparse の Namespace を模倣する SimpleNamespace を生成する。"""
    return SimpleNamespace(**kwargs)
