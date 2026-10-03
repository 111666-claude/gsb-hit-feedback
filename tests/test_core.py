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
