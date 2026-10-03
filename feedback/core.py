"""伤害飘字：同目标时间窗合并、数量上限、过期清理与稳定排序。

缺陷：同一目标的多次伤害不合并、飘字数量不设上限、过期条目不清、
结果按插入顺序、每次查询扫描全部记录。
"""


class Numbers:
    """伤害飘字台账。"""

    def __init__(self, merge_ms, max_numbers):
        self.merge_ms = merge_ms
        self.max_numbers = max_numbers
        self.entries = []
        self.scanned = 0

    def hit(self, target, amount, at_ms):
        """记录一次伤害。"""
        self.scanned += len(self.entries)
        self.entries.append({"target": target, "total": amount, "count": 1, "at": at_ms})
        return True

    def floats(self, now_ms):
        """返回当前应该显示的飘字。"""
        self.scanned += len(self.entries)
        return [(entry["target"], entry["total"], entry["count"]) for entry in self.entries]

    def count(self):
        return len(self.entries)

    def scanned_count(self):
        return self.scanned
