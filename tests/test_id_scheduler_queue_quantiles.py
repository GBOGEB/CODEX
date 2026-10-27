"""Native queue quantile tests: metric denominators, tails and authority isolation."""
import unittest

from scripts.id_work_conserving_scheduler import Item, summarize


class SchedulerQuantileTests(unittest.TestCase):
    def sample(self, ages):
        return summarize([Item(id=str(i), state="QUEUED", age_s=a)
                          for i, a in enumerate(ages)], pool_size=5)

    def test_even_cohort_p50_is_interpolated_median_not_upper_middle(self):
        x = self.sample([100.0, 1.0])
        self.assertEqual(x["queue_age_sample_count"], 2)
        self.assertEqual(x["p50_queue_age_s"], 50.5)
        self.assertEqual(x["p95_queue_age_s"], 100.0)

    def test_p95_nearest_rank_for_twenty_independent_queue_items(self):
        x = self.sample(list(range(1, 21)))
        self.assertEqual(x["queue_age_sample_count"], 20)
        self.assertEqual(x["p50_queue_age_s"], 10.5)
        self.assertEqual(x["p95_queue_age_s"], 19)
        self.assertEqual(x["max_queue_age_s"], 20)

    def test_empty_queue_does_not_fabricate_tail(self):
        x = self.sample([])
        self.assertEqual(x["queue_age_sample_count"], 0)
        self.assertIsNone(x["p95_queue_age_s"])
        self.assertEqual(x["p50_queue_age_s"], 0.0)
        self.assertEqual(x["queue_depth"], 0)

    def test_running_items_do_not_contaminate_queued_age_cohort(self):
        items = [Item(id="queued", age_s=5),
                 Item(id="active", state="RUNNING", age_s=1000)]
        x = summarize(items, pool_size=3)
        self.assertEqual((x["queue_depth"], x["running_depth"]), (1, 1))
        self.assertEqual(x["p95_queue_age_s"], 5)
        self.assertEqual(x["queue_age_sample_count"], 1)

    def test_metrics_do_not_claim_engineering_authority(self):
        x = self.sample([5, 10])
        self.assertEqual(x["authority_mutation"], "SERIALIZED_OUTSIDE_WORKER_POOL")
        self.assertTrue(x["pool"]["workers_reusable_across_pulses"])
        self.assertEqual(x["pool"]["execution_slots"], 4)


if __name__ == "__main__":
    unittest.main()
