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
2026-07-20 08:54:16 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · verified=True · via=api-patch · inbound-agegender+mpl-fix
2026-07-20 09:05:34 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · verified=True · via=api-patch · agegender-recheck+mpl-out
2026-07-20 09:05:34 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · verified=True · via=api-patch · agegender-recheck+mpl-out
2026-07-20 09:05:34 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · verified=True · via=api-patch · agegender-recheck+mpl-out
2026-07-20 09:05:34 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · verified=True · via=api-patch · agegender-recheck+mpl-out
2026-07-20 09:05:34 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · verified=True · via=api-patch · agegender-recheck+mpl-out
2026-07-20 09:35:08 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:40f2e811 · snapshot:pre-deploy-kkb-hi-out-2026-07-20_093507 · deployed
2026-07-20 09:35:08 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:1b2d9f01 · snapshot:pre-deploy-kkb-kn-out-2026-07-20_093508 · deployed
2026-07-20 09:35:09 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:5c016d78 · snapshot:pre-deploy-kkb-hi-in-2026-07-20_093508 · deployed
2026-07-20 09:35:09 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:7c02d871 · snapshot:pre-deploy-kkb-kn-in-2026-07-20_093509 · deployed
2026-07-20 09:35:10 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:ad87aa65 · snapshot:pre-deploy-maya-hi-out-2026-07-20_093509 · deployed
2026-07-20 09:35:10 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:6e03a5d0 · snapshot:pre-deploy-maya-hi-in-2026-07-20_093510 · deployed
2026-07-20 09:48:22 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:fa884e10 · snapshot:pre-deploy-kkb-hi-out-2026-07-20_094822 · deployed
2026-07-20 09:48:23 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:90c99ff0 · snapshot:pre-deploy-kkb-kn-out-2026-07-20_094823 · deployed
2026-07-20 09:48:24 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:dca43c3a · snapshot:pre-deploy-kkb-hi-in-2026-07-20_094823 · deployed
2026-07-20 09:48:24 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:6f0b0ee6 · snapshot:pre-deploy-kkb-kn-in-2026-07-20_094824 · deployed
2026-07-20 09:48:25 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:58554ce4 · snapshot:pre-deploy-maya-hi-out-2026-07-20_094825 · deployed
2026-07-20 09:48:25 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:d9ba68b2 · snapshot:pre-deploy-maya-hi-in-2026-07-20_094825 · deployed
