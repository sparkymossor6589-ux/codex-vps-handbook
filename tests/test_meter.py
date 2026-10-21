# Project provenance: local Codex-assisted maintenance/preview code.
# Scope and modifications: CONTRIBUTIONS.md and data/file-provenance.json.
# MIT applies only to rights held by project contributors; see LICENSE_SCOPE.md.
import copy
import datetime as dt
from traffic_service import accumulate, next_month

UTC = dt.timezone.utc
t = dt.datetime(2026, 10, 21, tzinfo=UTC)
s = accumulate(None, 'boot1', 100, 200, t)
assert (s['rx'], s['tx']) == (100, 200)
s = accumulate(s, 'boot1', 150, 260, t)
assert (s['rx'], s['tx']) == (150, 260)
# Process restart resumes without counting the interface baseline again.
s = accumulate(copy.deepcopy(s), 'boot1', 175, 280, t)
assert (s['rx'], s['tx']) == (175, 280)
# A machine reboot can produce larger NEW counters than the previous boot.
s = accumulate(s, 'boot2', 1000, 2000, t)
assert (s['rx'], s['tx']) == (1175, 2280)
s = accumulate(s, 'boot2', 1040, 2070, dt.datetime(2026, 11, 1, tzinfo=UTC))
assert (s['rx'], s['tx']) == (40, 70)
assert s['previous_month']['rx'] == 1175
assert next_month(dt.datetime(2026, 12, 31, tzinfo=UTC)) == dt.datetime(2027, 1, 1, tzinfo=UTC)
print('PASS: baseline, delta, process restart, reboot, monthly reset, year rollover')
