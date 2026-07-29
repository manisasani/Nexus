# Technical Debt

This file tracks known shortcuts, deferred optimizations, and incomplete
contracts made during development. Each item is intentional and documented
here so it isn't forgotten or mistaken for an oversight.

---

## 1. Project list N+1 query (owner)

**Where:** `ProjectViewSet.get_queryset()` in `apps/projects/views.py`

**Issue:** Each project row triggers a separate query for its owner when
serializing `owner_email`.

**Impact:** Low at current data volume (Phase 2 demo data).

**Fix:** Add `.select_related('owner')` to the queryset.

**Status:** Not yet applied. Fix in Phase 2 Step 9 or Phase 19 (performance pass).

---

## 2. Proposal list N+1 queries (freelancer, project)

**Where:** `ProposalViewSet.get_queryset()` in `apps/projects/views.py`

**Issue:** Listing proposals on a project serializes `freelancer` (email)
and `project` (title) for each row. Without `select_related`, each row
triggers separate queries for its related `freelancer` and `project`
objects — same N+1 pattern as the project list above.

**Impact:** Low at current data volume.

**Fix:** Add `.select_related('freelancer', 'project')` to the queryset:

```python
def get_queryset(self):
    project = get_object_or_404(Project, id=self.kwargs["project_id"])
    user = self.request.user
    qs = Proposal.objects.select_related('freelancer', 'project')

    if project.owner_id == user.id:
        return qs.filter(project=project)
    return qs.filter(project=project, freelancer=user)
```

**Status:** Not yet applied. Fix in Phase 2 Step 9 or Phase 19.

---

## 3. ACCEPTED proposal status has no real contract behind it

**Where:** `Proposal.status` field and `accept` action in `ProposalViewSet`

**Issue:** Setting a proposal's status to `ACCEPTED` currently only changes
a label on the record. It does not create a contract, lock the project,
reject competing proposals, trigger any payment/escrow flow, or notify
anyone. It is cosmetic for Phase 2 demo purposes only.

**Impact:** Medium — could mislead anyone assuming ACCEPTED implies a
binding agreement or triggers downstream business logic.

**Fix:** Full contract/acceptance workflow (locking the project, auto-rejecting
other proposals, payment integration) is planned for a later phase.

**Status:** Documented as known limitation. Full implementation deferred to Phase 8.

---

## 4. JWT Authentication token storage strategy

**Where:** Authentication layer (`apps/accounts/`)

**Issue:** JWT authentication is implemented using `djangorestframework-simplejwt`,
but the final frontend token storage strategy has not been decided yet.

Storing JWT tokens in browser localStorage can expose tokens to XSS attacks.

**Impact:** Medium for production applications where a frontend client is connected.

**Fix:** Use a production-safe strategy such as storing refresh tokens in
HttpOnly Secure cookies and keeping access tokens short-lived.

**Status:** Backend JWT implementation is complete. Frontend storage decision
is deferred until frontend integration.

---

## 5. Throttling uses in-memory storage

**Where:** Authentication throttling (`LoginRateThrottle`, `RegisterRateThrottle`)

**Issue:** API rate limiting currently relies on Django's default cache
backend, which is suitable for local development and single-instance
deployments.

In a distributed environment with multiple application servers, each server
would maintain its own throttle state, meaning rate limits would not be
shared globally.

**Impact:** Low for current development stage, but can become a security
concern when scaling horizontally.

**Fix:** Replace the default cache backend with a distributed cache such as
Redis so all application instances share the same throttle state.

**Status:** Intentionally deferred. Redis-based throttling will be considered
during production deployment.


## 6. No automated test suite

**Where:** Entire `apps/projects/` app (and `apps/accounts/`)

**Issue:** All Phase 2 verification so far has been manual — via Django
admin, the browsable API, and the `.http` demo file
(`http/.http`). There are no unit tests for models, serializers,
permissions, or views, and no integration tests for the full
project → proposal → accept/reject flow.

**Impact:** Medium — regressions could be introduced silently while
building later phases (JWT auth, additional apps) without any automated
signal.

**Fix:** Write unit tests (model validation, serializer validation,
permission classes) and integration tests (full API flows, including
failure paths already covered manually in `http/.http`).

**Status:** Deferred. Planned for Phase 7.

## 6. No auto-generated client SDKs

**Issue:** Frontend/mobile clients must hand-write API calls based on the
OpenAPI schema. No SDK generation pipeline exists yet.

**Status:** Intentionally postponed — not required for Phase 4 milestone.

## 7. 422 vs 400 not distinguished

**Issue:** All validation and business-rule errors return 400, following
DRF's default convention, rather than distinguishing syntactically invalid
requests (400) from semantically invalid ones (422).

**Status:** Intentional simplification for Phase 4. Revisit if API consumers
need finer-grained error handling.

## 10. No Redis or Celery containers yet

**Issue:** Docker Compose currently only orchestrates `web` and `db`.
Redis (caching, Celery broker) and Celery workers are not yet
containerized.

**Status:** Intentionally postponed. Redis in Phase 9, Celery in Phase 10.

## 11. No production-grade static file serving

**Issue:** `collectstatic` runs in entrypoint, but there's no reverse
proxy (nginx) or CDN serving static files — Gunicorn serves them directly
for now, which is not ideal for production traffic.

**Status:** Acceptable for current phase. Revisit when deploying to a
real production environment.

## 12. Race condition tests may behave differently on SQLite vs PostgreSQL

**Issue:** `test_accept_race_condition.py` tests concurrent access using
threads. SQLite's locking model (whole-database lock) differs from
PostgreSQL's row-level locking, which `select_for_update()` relies on.

**Status:** Test suite currently runs on SQLite for speed (Phase 7 decision).
This specific test should be verified against real PostgreSQL periodically,
or moved to a dedicated integration test suite that runs against Postgres.

## 13. Dispute resolution is a flag only

**Issue:** Raising a dispute marks the contract as DISPUTED but has no
resolution workflow, no admin ticketing, and no automatic escalation.

**Status:** Intentionally basic for Phase 8. Full ticketing system
planned for Phase 13.

## 14. No escrow or milestone payments yet

**Issue:** `agreed_price` is stored but no money actually moves. Contract
completion has no financial consequence yet.

**Status:** Intentionally postponed — escrow and milestone payments are
future phases, not part of Phase 8's scope.
## 15. Wallet balance cache not yet using Redis

**Issue:** `Wallet.balance` is stored and read directly from PostgreSQL.
Redis was provisioned (Step 3) but balance reads are not yet cached
through it — this was deferred to keep the ledger logic simple and
correct first.

**Status:** Acceptable for current traffic. Revisit if wallet read
volume becomes a bottleneck.

## 16. No real payment gateway or bank withdrawal

**Issue:** All money is internal/simulated. There is no connection to
Stripe, PayPal, or any real payment processor, and no ability to
withdraw to a real bank account.

**Status:** Intentionally postponed — this phase's goal was to get the
ledger logic correct before introducing external payment failure modes.

## 17. Concurrent debit test may behave differently on SQLite vs PostgreSQL

**Issue:** Same caveat as Phase 8's race condition test — `select_for_update()`
row-level locking relies on PostgreSQL behavior not fully replicated by SQLite.

**Status:** Verify periodically against real PostgreSQL.
## 18. Concurrent access tests skipped on SQLite

**Issue:** `test_concurrent_accept_only_creates_one_contract` and
`test_two_simultaneous_debits_cannot_overdraw` are marked `@pytest.mark.skip`
because SQLite's locking model does not reliably reproduce PostgreSQL's
row-level `select_for_update()` behavior under threading in the test suite.

**Status:** Both tests should be run manually against real PostgreSQL
(e.g. via `docker compose exec web pytest apps/wallets/tests/test_concurrent_debit.py --no-skip`
or a dedicated Postgres-backed test settings file) before considering
Phase 9's concurrency guarantees fully verified.

## 19. No dead-letter queue or task monitoring dashboard

**Issue:** Failed tasks (after exhausting retries) are only visible in
worker logs. There's no Flower dashboard or persistent dead-letter queue
for tracking permanently failed tasks.

**Status:** Acceptable for current scale. Consider adding Flower
(`celery flower`) or a dead-letter table if notification reliability
becomes critical.

## 20. Celery Beat has no scheduled tasks yet

**Issue:** The beat container runs but has zero periodic tasks configured
— it was provisioned ahead of need per Phase 10's design.

**Status:** Intentional. Will be used when periodic tasks (e.g. digest
emails, cleanup jobs) are introduced in a later phase.

## 21. New phone-based users get a default role without explicit choice

**Issue:** `OTPVerifyView` assigns `role=FREELANCER` by default to newly
created phone-based accounts, without asking the user to choose CLIENT
vs FREELANCER.

**Status:** Acceptable simplification for Phase 11. A proper onboarding
step (role selection after first OTP login) should be added before this
becomes a primary registration path.

## 22. purge_expired_otps task is currently a no-op

**Issue:** Since OTPs are stored in Redis with TTL, this scheduled task
does nothing meaningful yet — it exists as a placeholder for future
metrics/logging.

**Status:** Intentional. Revisit if OTP analytics become necessary.

## 23. No SLA timers or CSAT surveys

**Status:** Intentionally postponed per Phase 13 scope.

## 24. No AI auto-reply suggestions for staff

**Status:** Intentionally postponed per Phase 13 scope.

## 25. Ticket categories are fixed choices, not admin-configurable

**Issue:** `Ticket.Category` is a hardcoded TextChoices enum. Adding a
new category requires a code change + migration, not an admin UI change.

**Status:** Acceptable for current scale. Revisit if category needs
change frequently.