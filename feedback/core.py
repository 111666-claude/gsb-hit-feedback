"""伤害飘字：同目标时间窗合并、数量上限、过期清理与稳定排序。

实现要点：
- 合并：同一目标距上一条飘字不超过 merge_ms（含正好等于）时合并，
  伤害累加、次数加一；否则另起一条替换旧飘字。
- 上限：max_numbers 在查询时强制执行，超出时丢掉最早产生的那条。
- 过期：查询时惰性清理——每次查询只检查距最后一次受伤最久的一条，
  达到 merge_ms 则移除，绝不扫描全部历史伤害。
- 顺序：结果按目标 id 升序返回。
"""

import heapq


class Numbers:
    """伤害飘字台账。"""

    def __init__(self, merge_ms, max_numbers):
        self.merge_ms = merge_ms
        self.max_numbers = max_numbers
        self._entries = {}
        self._by_at = []
        self._by_created = []
        self._seq = 0
        self._scanned = 0

    def hit(self, target, amount, at_ms):
        """记录一次伤害。"""
        entry = self._entries.get(target)
        if entry is not None and at_ms - entry[2] <= self.merge_ms:
            entry[0] += amount
            entry[1] += 1
            entry[2] = at_ms
        else:
            entry = [amount, 1, at_ms, self._seq]
            self._seq += 1
            self._entries[target] = entry
            heapq.heappush(self._by_created, (entry[3], target))
        heapq.heappush(self._by_at, (at_ms, target))
        return True

    def _oldest_entry(self):
        while self._by_at:
            at_ms, target = self._by_at[0]
            entry = self._entries.get(target)
            if entry is not None and entry[2] == at_ms:
                return at_ms, target
            heapq.heappop(self._by_at)
        return None

    def _expire_oldest(self, now_ms):
        oldest = self._oldest_entry()
        if oldest is None:
            return
        at_ms, target = oldest
        self._scanned += 1
        if now_ms - at_ms >= self.merge_ms:
            self._scanned += 1
            heapq.heappop(self._by_at)
            del self._entries[target]

    def _enforce_cap(self):
        while len(self._entries) > self.max_numbers and self._by_created:
            created, target = heapq.heappop(self._by_created)
            entry = self._entries.get(target)
            if entry is not None and entry[3] == created:
                del self._entries[target]

    def floats(self, now_ms):
        """返回当前应该显示的飘字，按目标 id 升序。"""
        self._expire_oldest(now_ms)
        self._enforce_cap()
        return [
            (target, entry[0], entry[1])
            for target, entry in sorted(self._entries.items())
        ]

    def count(self):
        return len(self._entries)

    def scanned_count(self):
        return self._scanned
