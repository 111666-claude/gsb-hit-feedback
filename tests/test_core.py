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
        world.hit("mob", 30, 200)
        self.assertEqual(world.floats(200), [("mob", 60, 3)])

    def test_exact_window_edge_merges(self):
        world = numbers()
        world.hit("mob", 10, 0)
        world.hit("mob", 20, 300)
        self.assertEqual(world.floats(300), [("mob", 30, 2)])

    def test_beyond_window_starts_new_entry(self):
        world = numbers()
        world.hit("mob", 10, 0)
        world.hit("mob", 20, 301)
        self.assertEqual(world.floats(301), [("mob", 20, 1)])

    def test_merge_does_not_cross_targets(self):
        world = numbers()
        world.hit("a", 10, 0)
        world.hit("b", 20, 10)
        self.assertEqual(world.floats(10), [("a", 10, 1), ("b", 20, 1)])


class CapTest(unittest.TestCase):
    def test_display_never_exceeds_max(self):
        world = Numbers(merge_ms=100000, max_numbers=2)
        for index in range(3):
            world.hit("mob-%d" % index, 10, index * 10)
        self.assertEqual(len(world.floats(30)), 2)

    def test_cap_drops_earliest_created(self):
        world = Numbers(merge_ms=100000, max_numbers=2)
        world.hit("m0", 10, 0)
        world.hit("m1", 10, 10)
        world.hit("m2", 10, 20)
        self.assertEqual(world.floats(30), [("m1", 10, 1), ("m2", 10, 1)])


class TtlTest(unittest.TestCase):
    def test_fresh_entry_survives(self):
        world = Numbers(merge_ms=100, max_numbers=8)
        world.hit("mob", 10, 0)
        self.assertEqual(world.floats(99), [("mob", 10, 1)])

    def test_entry_expires_exactly_at_merge_ms(self):
        world = Numbers(merge_ms=100, max_numbers=8)
        world.hit("mob", 10, 0)
        self.assertEqual(world.floats(100), [])

    def test_expiry_is_amortized_one_per_query(self):
        world = Numbers(merge_ms=100, max_numbers=8)
        world.hit("a", 10, 0)
        world.hit("b", 10, 0)
        self.assertEqual(len(world.floats(1000)), 1)
        self.assertEqual(world.floats(1000), [])


class OrderTest(unittest.TestCase):
    def test_results_sorted_by_target(self):
        world = Numbers(merge_ms=100000, max_numbers=8)
        world.hit("zebra", 10, 0)
        world.hit("alpha", 10, 10)
        world.hit("mike", 10, 20)
        rows = world.floats(30)
        self.assertEqual([row[0] for row in rows], ["alpha", "mike", "zebra"])

    def test_order_independent_of_insertion(self):
        first = Numbers(merge_ms=100000, max_numbers=8)
        second = Numbers(merge_ms=100000, max_numbers=8)
        for target in ("zebra", "alpha", "mike"):
            first.hit(target, 10, 0)
        for target in ("mike", "alpha", "zebra"):
            second.hit(target, 10, 0)
        self.assertEqual(first.floats(0), second.floats(0))


class InvariantTest(unittest.TestCase):
    def test_count_equals_merged_hits(self):
        world = numbers()
        for index in range(5):
            world.hit("mob", 10, index * 100)
        self.assertEqual(world.floats(400), [("mob", 50, 5)])

    def test_same_sequence_same_result(self):
        def run():
            world = Numbers(merge_ms=300, max_numbers=4)
            world.hit("b", 10, 0)
            world.hit("a", 20, 50)
            world.hit("b", 30, 100)
            world.hit("a", 40, 500)
            return world.floats(500)

        self.assertEqual(run(), run())


class ScanTest(unittest.TestCase):
    def test_floats_does_not_scan_history(self):
        world = Numbers(merge_ms=100000, max_numbers=1000)
        for index in range(100):
            world.hit("mob-%d" % index, 10, index)
        before = world.scanned_count()
        world.floats(100)
        self.assertEqual(world.scanned_count() - before, 1)

    def test_scanned_grows_with_operations_not_history(self):
        world = Numbers(merge_ms=1, max_numbers=10000)
        for index in range(3000):
            world.hit("mob-%d" % index, 10, index * 1000)
        for index in range(3000):
            world.floats(index * 1000)
        self.assertLessEqual(world.scanned_count(), 6000)
