from scripts.w05_worker_multiplier_plan import PARTITIONS, build_plan


def test_default_plan_matches_w05_power2_policy():
    plan = build_plan()
    assert plan["discovery_multiple_3pr"] == 16
    assert plan["mutation_multiple_3pr"] == 8
    assert plan["discovery_sue_capacity"] == 48
    assert plan["mutation_sue_capacity"] == 24
    assert plan["single_writer_registry"] is True


def test_discovery_workers_cover_all_partitions_twice():
    plan = build_plan(16, 8)
    discovery = [w for w in plan["workers"] if w["mode"] == "discovery"]
    assert len(discovery) == 16
    for partition in PARTITIONS:
        assert sum(w["partition"] == partition for w in discovery) == 2


def test_mutation_workers_cover_each_partition_once_and_cannot_write_registry():
    plan = build_plan(16, 8)
    mutation = [w for w in plan["workers"] if w["mode"] == "mutation_candidate"]
    assert len(mutation) == 8
    assert {w["partition"] for w in mutation} == set(PARTITIONS)
    assert all(w["registry_write"] is False for w in mutation)


def test_worker_ids_are_unique():
    plan = build_plan(16, 8)
    ids = [w["worker_id"] for w in plan["workers"]]
    assert len(ids) == len(set(ids))


def test_invalid_non_power_two_multiple_rejected():
    try:
        build_plan(12, 8)
    except ValueError as exc:
        assert "power" not in str(exc).lower() or "must be one of" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_mutation_cannot_exceed_discovery():
    try:
        build_plan(8, 16)
    except ValueError as exc:
        assert "cannot exceed" in str(exc)
    else:
        raise AssertionError("expected ValueError")
