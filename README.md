# hit-feedback

伤害飘字：同目标时间窗合并、数量上限、过期清理与稳定排序，只用 Python 标准库。

```
python3 -m feedback.cli --sample merge
python3 -m feedback.cli --sample cap
python3 -m feedback.cli --sample ttl
python3 -m feedback.cli --sample order
python3 -m feedback.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **合并**：同一目标距上一条飘字不足 `merge_ms` 时合并进同一条，伤害累加、次数加一；
  正好等于 `merge_ms` 也算合并。
- **上限**：同时在显示的飘字不超过 `max_numbers`，超出时丢掉最早产生的那条。
- **过期**：距最后一次受伤达到 `merge_ms` 的飘字在查询时移除。
- **顺序**：结果按目标 id 升序返回。
- **不变量**：`count` 等于合并进来的伤害次数；同一串伤害序列重复执行结果相同。
- **代价**：`floats` 不许扫描全部历史伤害，`scanned_count` 不随伤害数线性增长。
- **规模**：10 万次伤害、每秒 10 万次查询，单次摊还 O(活跃飘字数)。

## 输出契约（不改格式）

```
entries=.. total=..
entries=..
first=..
scanned=..
```

## 目录

```
feedback/core.py   合并、上限、过期与排序
feedback/cli.py    命令行入口
tests/             unittest 用例
```
