"""Dated public budget checks use only synthetic temporary ledgers."""
from datetime import datetime, timezone
import sqlite3

import pytest

import backend.hosting as hosting
from backend.hosting import PublicLimits


@pytest.fixture
def clock(monkeypatch):
    class Clock(datetime):
        day = '2026-10-29'

        @classmethod
        def now(cls, tz):
            assert tz is timezone.utc
            return datetime.fromisoformat(cls.day + 'T12:00:00+00:00')

    monkeypatch.setattr(hosting, 'datetime', Clock)
    return Clock


def test_hackathon_opt_in_and_expiry_without_restart(tmp_path):
    ordinary = PublicLimits(tmp_path)
    limits = PublicLimits(tmp_path, release_allowance=True, hackathon_allowance=True)
    assert ordinary.effective_limits('2026-10-29') == (100, 5_000_000)
    assert limits.effective_limits('2026-10-28') == (160, 15_300_000)
    for day in ('2026-10-29', '2026-10-30', '2026-10-31'):
        assert limits.effective_limits(day) == (500, 50_000_000)
    assert limits.effective_limits('2026-11-01') == (100, 5_000_000)
    assert limits.effective_limits('2027-10-29') == (100, 5_000_000)


@pytest.mark.parametrize('bound', ['daily', 'monthly'])
def test_hackathon_preserves_prior_spend_and_refuses_at_hard_cap(tmp_path, clock, bound):
    limits = PublicLimits(tmp_path, hackathon_allowance=True)
    assert limits.reserve_stage(1, clock.day, 'a' * 32, 'draft')['reserved']
    with sqlite3.connect(tmp_path / 'answer-usage.sqlite') as db:
        db.execute('INSERT INTO usage VALUES (?,158)', ('2026-10-28',))
        db.execute('UPDATE usage SET attempts=499 WHERE day=?', (clock.day,))
        db.execute('UPDATE spend SET reserved_microusd=?', (15_026_637 if bound == 'daily' else 49_800_000,))
    limits = PublicLimits(tmp_path, require_existing=True, hackathon_allowance=True)
    receipt = limits.reserve_stage(112_704, clock.day, 'b' * 32, 'draft')
    assert receipt['reserved']
    with sqlite3.connect(tmp_path / 'answer-usage.sqlite') as db:
        if bound == 'monthly':
            db.execute('UPDATE usage SET attempts=2 WHERE day=?', (clock.day,))
        before = list(db.iterdump())
    refusal = limits.reserve_stage(112_704, clock.day, 'c' * 32, 'draft')
    assert refusal['reason'] == bound + '_limit'
    with sqlite3.connect(tmp_path / 'answer-usage.sqlite') as db:
        assert list(db.iterdump()) == before
        assert db.execute('SELECT attempts FROM usage WHERE day=?', ('2026-10-28',)).fetchone()[0] == 158
        assert db.execute('SELECT count(*) FROM stage_reservations').fetchone()[0] == 2
    clock.day = '2026-11-01'
    assert limits.reserve_stage(5_000_001, clock.day, 'd' * 32, 'draft')['reason'] == 'monthly_limit'


def test_app_requires_explicit_hackathon_flag(tmp_path, monkeypatch):
    import backend.app as app_module
    captured = []

    def capture(*args, **kwargs):
        limits = PublicLimits(*args, **kwargs)
        captured.append(limits)
        return limits

    monkeypatch.setattr(app_module, 'PublicLimits', capture)
    monkeypatch.delenv('RESEARCH_PUBLIC_ORIGIN', raising=False)
    monkeypatch.delenv('RESEARCH_HACKATHON_ALLOWANCE_20261029', raising=False)
    app_module.create_app(root=tmp_path)
    assert not captured[-1].hackathon_allowance
    monkeypatch.setenv('RESEARCH_HACKATHON_ALLOWANCE_20261029', '1')
    app_module.create_app(root=tmp_path)
    assert captured[-1].effective_limits('2026-10-29') == (500, 50_000_000)
    assert captured[-1].effective_limits('2026-11-01') == (100, 5_000_000)
