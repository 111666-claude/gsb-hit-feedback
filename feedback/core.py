"""伤害飘字：同目标时间窗合并、数量上限、过期清理与稳定排序。

口径（README 为准）：
- 合并：同一目标距上一条飘字不足 merge_ms 时合并（正好等于也算），
  伤害累加、次数加一。
- 上限：同时在显示的飘字不超过 max_numbers，超出时丢掉最早产生的那条。
- 过期：距最后一次受伤达到 merge_ms 的飘字在查询时移除；为保持摊还 O(1)，
  每次查询清理一条最早产生的过期飘字。
- 顺序：结果按目标 id 升序返回。
- 代价：不保留全部历史伤害，scanned_count 随操作次数增长，不随历史大小增长。
"""

from collections import deque


class Numbers:
    """伤害飘字台账。"""

    def __init__(self, merge_ms, max_numbers):
        self.merge_ms = merge_ms
        self.max_numbers = max_numbers
        self._active = {}  # target -> {"total", "count", "last_at", "seq"}
        self._order = deque()  # (seq, target)，按产生先后，允许惰性失效
        self._seq = 0
        self.scanned = 0

    def hit(self, target, amount, at_ms):
        """记录一次伤害。"""
        self.scanned += 1
        entry = self._active.get(target)
        if entry is not None and at_ms - entry["last_at"] <= self.merge_ms:
            entry["total"] += amount
            entry["count"] += 1
            if at_ms > entry["last_at"]:
                entry["last_at"] = at_ms
            return True
        self._seq += 1
        self._active[target] = {
            "total": amount,
            "count": 1,
            "last_at": at_ms,
            "seq": self._seq,
        }
        self._order.append((self._seq, target))
        return True

    def floats(self, now_ms):
        """返回当前应该显示的飘字，按目标 id 升序。"""
        self.scanned += 1
        self._expire_one(now_ms)
        self._enforce_cap()
        rows = sorted(self._active.items(), key=lambda item: item[0])
        return [(target, entry["total"], entry["count"]) for target, entry in rows]

    def _expire_one(self, now_ms):
        """每次查询摊还清理一条最早产生的过期飘字。"""
        while self._order:
            seq, target = self._order[0]
            entry = self._active.get(target)
            if entry is None or entry["seq"] != seq:
                self._order.popleft()  # 已被替换或清理的惰性节点
                continue
            if now_ms - entry["last_at"] >= self.merge_ms:
                del self._active[target]
                self._order.popleft()
            break

    def _enforce_cap(self):
        """显示条数超过 max_numbers 时，丢掉最早产生的那条。"""
        while len(self._active) > self.max_numbers and self._order:
            seq, target = self._order.popleft()
            entry = self._active.get(target)
            if entry is None or entry["seq"] != seq:
                continue
            del self._active[target]

    def count(self):
        return len(self._active)

    def scanned_count(self):
        return self.scanned
