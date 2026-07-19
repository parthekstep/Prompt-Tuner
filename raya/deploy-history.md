# Raya deploy history

Append-only log of prompts pushed live via `scripts/raya_deploy.py deploy`.
Newest entries at the bottom. This records what went live, when, and the
pre-deploy snapshot label to roll back to — the deploy-side twin of
`versions/<Agent>/HISTORY.md` (which logs edits, not deploys).

This is **not** an edit log — prompt *edits* go in each agent's `CHANGELOG.md`.
A deploy ships whatever is already on disk; it does not change prompt content.

Format:
`YYYY-MM-DD HH:MM:SS · <env> · <target-id> · <raya_agent_id> · <file> · sha256:<8> · snapshot:<label> · <result>`

---
2026-07-18 19:59:01 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · verified=True · via=api-patch
2026-07-18 19:59:01 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · verified=True · via=api-patch
2026-07-18 19:59:01 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · verified=True · via=api-patch
2026-07-18 19:59:01 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · verified=True · via=api-patch
2026-07-18 19:59:01 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · verified=True · via=api-patch
2026-07-18 19:59:01 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · verified=True · via=api-patch
2026-07-19 16:54:19 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · verified=True · via=api-patch · MPL-feature
2026-07-19 16:54:19 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · verified=True · via=api-patch · MPL-feature
2026-07-19 17:22:03 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:22:03 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:22:03 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:22:03 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:22:03 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:22:03 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:32:47 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · verified=True · via=api-patch · mpl-english+wording-fix
2026-07-19 17:32:47 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · verified=True · via=api-patch · mpl-english+wording-fix
2026-07-19 17:32:47 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · verified=True · via=api-patch · mpl-english+wording-fix
2026-07-19 17:32:47 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · verified=True · via=api-patch · mpl-english+wording-fix
