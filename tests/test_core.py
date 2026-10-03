import unittest

from feedback.core import Numbers


def numbers():
    return Numbers(merge_ms=300, max_numbers=4)


class BasicTest(unittest.TestCase):
    def test_empty_floats(self):
        self.assertEqual(numbers().floats(0), [])

    def test_single_hit(self):
        world = numbers()
        world.hit("mob", 10, 0)
        self.assertEqual(world.floats(0), [("mob", 10, 1)])

    def test_count_starts_at_zero(self):
        self.assertEqual(numbers().count(), 0)

    def test_merge_ms_is_stored(self):
        self.assertEqual(numbers().merge_ms, 300)

    def test_scanned_starts_at_zero(self):
        self.assertEqual(numbers().scanned_count(), 0)


if __name__ == "__main__":
    unittest.main()


class MergeTest(unittest.TestCase):
    def test_hits_within_window_merge(self):
        world = numbers()
        world.hit("mob", 10, 0)
        world.hit("mob", 20, 100)
        self.assertEqual(world.floats(100), [("mob", 30, 2)])

    def test_hit_exactly_at_window_merges(self):
        world = numbers()
        world.hit("mob", 10, 0)
        world.hit("mob", 20, 300)
        self.assertEqual(world.floats(300), [("mob", 30, 2)])

    def test_hit_beyond_window_starts_new_entry(self):
        world = numbers()
        world.hit("mob", 10, 0)
        world.hit("mob", 20, 301)
        self.assertEqual(world.floats(301), [("mob", 20, 1)])

    def test_merges_only_same_target(self):
        world = numbers()
        world.hit("a", 10, 0)
        world.hit("b", 20, 0)
        self.assertEqual(world.floats(0), [("a", 10, 1), ("b", 20, 1)])

    def test_three_hits_total_and_count(self):
        world = numbers()
        world.hit("mob", 10, 0)
        world.hit("mob", 20, 100)
        world.hit("mob", 30, 200)
        self.assertEqual(world.floats(200), [("mob", 60, 3)])


class CapTest(unittest.TestCase):
    def test_display_never_exceeds_max(self):
        world = numbers()
        for index in range(6):
            world.hit("mob-%d" % index, 10, index)
        rows = world.floats(6)
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            [row[0] for row in rows], ["mob-2", "mob-3", "mob-4", "mob-5"]
        )

    def test_cap_keeps_most_recent_entries(self):
        world = Numbers(merge_ms=1, max_numbers=2)
        for index in range(3):
            world.hit("mob-%d" % index, 10, index * 1000)
        self.assertEqual(len(world.floats(3000)), 2)


class TtlTest(unittest.TestCase):
    def test_entry_at_merge_boundary_is_removed(self):
        world = numbers()
        world.hit("mob", 10, 0)
        self.assertEqual(world.floats(300), [])

    def test_entry_just_inside_window_is_kept(self):
        world = numbers()
        world.hit("mob", 10, 0)
        self.assertEqual(world.floats(299), [("mob", 10, 1)])

    def test_expired_entries_are_cleared_lazily(self):
        world = Numbers(merge_ms=1, max_numbers=8)
        world.hit("a", 10, 0)
        world.hit("b", 10, 1)
        self.assertEqual(world.floats(1000), [("b", 10, 1)])
        self.assertEqual(world.floats(1000), [])


class OrderTest(unittest.TestCase):
    def test_floats_sorted_by_target_id(self):
        world = numbers()
        world.hit("zebra", 10, 0)
        world.hit("alpha", 10, 1)
        rows = world.floats(2)
        self.assertEqual([row[0] for row in rows], ["alpha", "zebra"])


class InvariantTest(unittest.TestCase):
    def test_count_equals_merged_hit_times(self):
        world = numbers()
        for amount, at_ms in [(10, 0), (20, 100), (30, 200), (40, 250)]:
            world.hit("mob", amount, at_ms)
        self.assertEqual(world.floats(250)[0][2], 4)

    def test_same_hit_sequence_replays_identically(self):
        def run():
            world = numbers()
            world.hit("b", 10, 0)
            world.hit("a", 20, 100)
            world.hit("b", 30, 200)
            return world.floats(200)
        self.assertEqual(run(), run())

    def test_scanned_does_not_scale_with_hit_count(self):
        world = Numbers(merge_ms=1, max_numbers=10000)
        for index in range(3000):
            world.hit("mob-%d" % index, 10, index * 1000)
        for index in range(3000):
            world.floats(index * 1000)
        self.assertLessEqual(world.scanned_count(), 6000)
