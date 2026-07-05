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

## 4. Authentication is temporary (Session/Basic, not JWT)

**Where:** `REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]` in `config/settings`

**Issue:** Phase 2 API testing and demo currently rely on
`SessionAuthentication` and `BasicAuthentication`. JWT authentication has
not been implemented yet, so `BasicAuthentication` is enabled purely for
local manual testing convenience (e.g. via `.http` files), which is not
suitable for production.

**Impact:** Low for now (local dev only), but `BasicAuthentication` must be
removed before any public/production deployment, since it sends
base64-encoded credentials on every request.

**Fix:** Replace with JWT authentication (e.g. `djangorestframework-simplejwt`)
in the authentication phase. No changes to views, permissions, or serializers
are expected — they operate on `request.user` regardless of how it was
authenticated.

**Status:** Deferred intentionally. Remove `BasicAuthentication` once JWT lands.

---

## 5. No automated test suite

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