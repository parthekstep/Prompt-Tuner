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
2026-07-20 10:00:57 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:6bd77a6e · snapshot:pre-deploy-maya-hi-in-2026-07-20_100057 · deployed
2026-07-20 10:00:58 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:a930a02a · snapshot:pre-deploy-maya-hi-out-2026-07-20_100058 · deployed
2026-07-20 10:11:49 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:b93e866b · snapshot:pre-deploy-maya-hi-in-2026-07-20_101149 · deployed
2026-07-20 10:11:50 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:0b553014 · snapshot:pre-deploy-maya-hi-out-2026-07-20_101150 · deployed
2026-07-20 10:26:02 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:5f420f09 · snapshot:pre-deploy-kkb-hi-out-2026-07-20_102601 · deployed
2026-07-20 10:26:02 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:caf1c0f7 · snapshot:pre-deploy-kkb-kn-out-2026-07-20_102602 · deployed
2026-07-20 10:26:04 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:9c852ae9 · snapshot:pre-deploy-kkb-hi-in-2026-07-20_102602 · deployed
2026-07-20 10:26:05 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:f373cf9c · snapshot:pre-deploy-kkb-kn-in-2026-07-20_102604 · deployed
2026-07-20 10:26:06 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:324ecfd0 · snapshot:pre-deploy-maya-hi-out-2026-07-20_102605 · deployed
2026-07-20 10:26:06 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:56b8bd0c · snapshot:pre-deploy-maya-hi-in-2026-07-20_102606 · deployed
2026-07-20 10:35:40 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ea448ac5 · snapshot:pre-deploy-kkb-hi-out-2026-07-20_103539 · deployed
2026-07-20 10:35:40 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:3cee2a34 · snapshot:pre-deploy-kkb-kn-out-2026-07-20_103540 · deployed
2026-07-20 10:35:42 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:82a042c3 · snapshot:pre-deploy-kkb-hi-in-2026-07-20_103541 · deployed
2026-07-20 10:35:43 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:ae8e9d61 · snapshot:pre-deploy-kkb-kn-in-2026-07-20_103542 · deployed
2026-07-20 10:35:43 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:b8f8eab1 · snapshot:pre-deploy-maya-hi-out-2026-07-20_103543 · deployed
2026-07-20 10:35:44 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:03e71608 · snapshot:pre-deploy-maya-hi-in-2026-07-20_103543 · deployed
2026-07-20 10:35:44 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:ddc84e64 · snapshot:pre-deploy-dkb-hi-out-2026-07-20_103544 · deployed
2026-07-20 10:35:45 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:3f200181 · snapshot:pre-deploy-dkb-kn-out-2026-07-20_103544 · deployed
2026-07-20 10:48:31 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:fd2eda94 · snapshot:pre-deploy-maya-hi-in-2026-07-20_104830 · deployed
2026-07-20 10:48:32 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:6b675eb1 · snapshot:pre-deploy-maya-hi-out-2026-07-20_104831 · deployed
2026-07-20 11:34:59 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:bc23c4ff · snapshot:pre-deploy-maya-hi-in-2026-07-20_113458 · deployed
2026-07-20 11:34:59 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e911b925 · snapshot:pre-deploy-maya-hi-out-2026-07-20_113459 · deployed
2026-07-20 12:36:39 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:bc23c4ff · snapshot:pre-deploy-maya-hi-in-2026-07-20_123639 · deployed
2026-07-20 12:38:16 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ea448ac5 · snapshot:- · skip-in-sync
2026-07-20 12:38:17 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:3cee2a34 · snapshot:- · skip-in-sync
2026-07-20 12:38:19 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:82a042c3 · snapshot:- · skip-in-sync
2026-07-20 12:38:19 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:ae8e9d61 · snapshot:- · skip-in-sync
2026-07-20 12:38:20 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e911b925 · snapshot:pre-deploy-maya-hi-out-2026-07-20_123819 · deployed
2026-07-20 12:38:20 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:bc23c4ff · snapshot:- · skip-in-sync
2026-07-20 12:38:20 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:ddc84e64 · snapshot:- · skip-in-sync
2026-07-20 12:38:21 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:3f200181 · snapshot:- · skip-in-sync
2026-07-20 12:39:06 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ea448ac5 · snapshot:- · skip-in-sync
2026-07-20 12:39:06 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:3cee2a34 · snapshot:- · skip-in-sync
2026-07-20 12:39:07 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:82a042c3 · snapshot:- · skip-in-sync
2026-07-20 12:39:08 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:ae8e9d61 · snapshot:- · skip-in-sync
2026-07-20 12:39:08 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e911b925 · snapshot:- · skip-in-sync
2026-07-20 12:39:08 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:bc23c4ff · snapshot:- · skip-in-sync
2026-07-20 12:39:08 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:ddc84e64 · snapshot:- · skip-in-sync
2026-07-20 12:39:09 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:3f200181 · snapshot:- · skip-in-sync
2026-07-20 12:39:35 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ea448ac5 · snapshot:- · skip-in-sync
2026-07-20 12:40:01 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ea448ac5 · snapshot:- · skip-in-sync
2026-07-20 12:40:01 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:3cee2a34 · snapshot:- · skip-in-sync
2026-07-20 12:40:02 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:82a042c3 · snapshot:- · skip-in-sync
2026-07-20 12:40:02 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:ae8e9d61 · snapshot:- · skip-in-sync
2026-07-20 12:40:02 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e911b925 · snapshot:- · skip-in-sync
2026-07-20 12:40:03 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:bc23c4ff · snapshot:- · skip-in-sync
2026-07-20 12:40:03 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:ddc84e64 · snapshot:- · skip-in-sync
2026-07-20 12:40:03 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:3f200181 · snapshot:- · skip-in-sync
2026-07-20 13:47:58 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:acc65013 · snapshot:pre-deploy-kkb-hi-out-2026-07-20_134756 · deployed
2026-07-20 13:47:59 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:847f7e06 · snapshot:pre-deploy-kkb-kn-out-2026-07-20_134758 · deployed
2026-07-20 13:48:01 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:e96cac5a · snapshot:pre-deploy-kkb-hi-in-2026-07-20_134800 · deployed
2026-07-20 13:48:03 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:a7cb1235 · snapshot:pre-deploy-kkb-kn-in-2026-07-20_134802 · deployed
2026-07-20 13:48:03 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:4058e05e · snapshot:pre-deploy-maya-hi-out-2026-07-20_134803 · deployed
2026-07-20 13:48:05 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:2ce4b7a5 · snapshot:pre-deploy-maya-hi-in-2026-07-20_134804 · deployed
2026-07-20 17:56:37 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:50437850 · snapshot:- · dry-run
2026-07-20 18:14:05 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:dad55800 · snapshot:pre-deploy-maya-hi-out-2026-07-20_181405 · deployed
2026-07-20 18:30:04 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:1a830d75 · snapshot:pre-deploy-maya-hi-out-2026-07-20_183000 · deployed
2026-07-20 18:49:54 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:9cf2877d · snapshot:pre-deploy-maya-hi-out-2026-07-20_184954 · deployed
2026-07-20 18:57:42 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:883c5e4d · snapshot:pre-deploy-maya-hi-out-2026-07-20_185739 · deployed
2026-07-20 19:08:40 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:64474648 · snapshot:pre-deploy-maya-hi-out-2026-07-20_190839 · deployed
2026-07-20 19:12:55 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:3b474e2c · snapshot:pre-deploy-maya-hi-out-2026-07-20_191253 · deployed
2026-07-20 19:17:40 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:2340b864 · snapshot:pre-deploy-maya-hi-out-2026-07-20_191738 · deployed
2026-07-20 19:23:15 · prod · maya-out-memory · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Memory.md · sha256:9c8f4e68 · snapshot:- · skip-in-sync
2026-07-20 19:24:21 · prod · maya-out-memory · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Memory.md · sha256:9c8f4e68 · snapshot:pre-deploy-maya-out-memory-2026-07-20_192418 · deployed
2026-07-20 19:24:46 · prod · maya-in-memory · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Memory.md · sha256:9c8f4e68 · snapshot:pre-deploy-maya-in-memory-2026-07-20_192446 · deployed
2026-07-22 11:40:34 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:cb374109 · snapshot:pre-deploy-kkb-hi-out-2026-07-22_114033 · deployed
2026-07-22 11:40:35 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:ba8d8907 · snapshot:pre-deploy-kkb-kn-out-2026-07-22_114035 · deployed
2026-07-22 12:47:45 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:330ae247 · snapshot:pre-deploy-kkb-hi-out-2026-07-22_124742 · deployed
2026-07-22 12:47:46 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:1b76f201 · snapshot:pre-deploy-kkb-kn-out-2026-07-22_124746 · deployed
2026-07-22 12:58:06 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:3310c32d · snapshot:pre-deploy-kkb-hi-in-2026-07-22_125804 · deployed
2026-07-22 12:58:07 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:4669eb7d · snapshot:pre-deploy-kkb-kn-in-2026-07-22_125807 · deployed
2026-07-22 13:00:43 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:d7dbb322 · snapshot:pre-deploy-maya-hi-out-2026-07-22_130038 · deployed
2026-07-22 13:30:21 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:16ef42f1 · snapshot:pre-deploy-dkb-hi-out-2026-07-22_133021 · deployed
2026-07-22 13:30:21 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:a5dbc7c1 · snapshot:pre-deploy-dkb-kn-out-2026-07-22_133021 · deployed
2026-07-22 13:47:15 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:236af7ef · snapshot:pre-deploy-kkb-hi-out-2026-07-22_134709 · deployed
2026-07-22 13:47:16 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:358d3607 · snapshot:pre-deploy-kkb-kn-out-2026-07-22_134715 · deployed
2026-07-22 16:40:09 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:74c900b1 · snapshot:pre-deploy-kkb-hi-in-2026-07-22_164005 · deployed
2026-07-22 16:40:13 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:e73018d5 · snapshot:pre-deploy-kkb-kn-in-2026-07-22_164011 · deployed
2026-07-22 17:19:13 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:23268495 · snapshot:pre-deploy-kkb-hi-in-2026-07-22_171859 · deployed
2026-07-22 17:19:25 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:ee29d045 · snapshot:pre-deploy-kkb-kn-in-2026-07-22_171917 · deployed
2026-07-22 17:24:37 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:fef972a0 · snapshot:pre-deploy-kkb-hi-in-2026-07-22_172359 · deployed
2026-07-22 17:25:06 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:09b414ed · snapshot:pre-deploy-kkb-kn-in-2026-07-22_172446 · deployed
2026-07-22 17:28:42 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:2ced8c59 · snapshot:pre-deploy-kkb-hi-in-2026-07-22_172748 · deployed
2026-07-22 17:29:17 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:7c98ea27 · snapshot:pre-deploy-kkb-kn-in-2026-07-22_172853 · deployed
2026-07-22 20:15:56 · prod · kkb-hi-in · 08001508-0146-467b-a35f-e8754a7aeff5 · KKB/KKB Placeholder Inbound.md · sha256:09e410ba · snapshot:pre-deploy-kkb-hi-in-2026-07-22_201555 · deployed
2026-07-22 20:18:09 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:7c98ea27 · snapshot:- · skip-in-sync
2026-07-22 20:18:10 · prod · kkb-hi-in · 08001508-0146-467b-a35f-e8754a7aeff5 · KKB/KKB Placeholder Inbound.md · sha256:09e410ba · snapshot:- · skip-in-sync
2026-07-22 22:31:43 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:61162c10 · snapshot:pre-deploy-kkb-hi-in-2026-07-22_223142 · deployed
2026-07-22 22:33:07 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:9d98a31c · snapshot:pre-deploy-kkb-kn-in-2026-07-22_223215 · deployed
2026-07-23 11:46:07 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:2ced8c59 · snapshot:pre-deploy-kkb-hi-in-2026-07-23_114607 · deployed
2026-07-23 11:47:50 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:7c98ea27 · snapshot:pre-deploy-kkb-kn-in-2026-07-23_114736 · FAILED-http-520
2026-07-27 00:56:40 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:9a31a31e · snapshot:pre-deploy-kkb-kn-in-2026-07-27_005640 · deployed
2026-07-27 00:56:41 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:7be20a47 · snapshot:pre-deploy-kkb-hi-out-2026-07-27_005641 · deployed
2026-07-27 00:56:42 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:9747ea41 · snapshot:pre-deploy-kkb-kn-out-2026-07-27_005642 · deployed
2026-07-27 00:56:42 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:5ada6513 · snapshot:pre-deploy-kkb-hi-in-2026-07-27_005642 · deployed
2026-07-27 00:56:44 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:d48b7e78 · snapshot:pre-deploy-maya-hi-out-2026-07-27_005643 · deployed
2026-07-27 00:56:44 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:209847d5 · snapshot:pre-deploy-maya-hi-in-2026-07-27_005644 · deployed
2026-07-27 01:15:23 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:c483d75a · snapshot:pre-deploy-kkb-hi-in-2026-07-27_011523 · deployed
2026-07-27 01:15:23 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:db86351f · snapshot:pre-deploy-kkb-kn-in-2026-07-27_011523 · deployed
2026-07-27 01:36:58 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:b257cb42 · snapshot:pre-deploy-maya-hi-out-2026-07-27_013658 · deployed
2026-07-27 01:36:58 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:e94b03fb · snapshot:pre-deploy-maya-hi-in-2026-07-27_013658 · deployed
2026-07-27 01:46:38 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:f91622b0 · snapshot:pre-deploy-kkb-kn-in-2026-07-27_014638 · deployed
2026-07-27 01:46:39 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:23feff4d · snapshot:pre-deploy-kkb-kn-out-2026-07-27_014639 · deployed
2026-07-27 01:46:39 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:2ca73049 · snapshot:pre-deploy-maya-hi-out-2026-07-27_014639 · deployed
2026-07-27 02:24:32 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:0fd202e7 · snapshot:pre-deploy-kkb-hi-out-2026-07-27_022432 · deployed
2026-07-27 02:24:32 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:2c7b11af · snapshot:pre-deploy-kkb-kn-out-2026-07-27_022432 · deployed
2026-07-27 02:24:33 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:a66c02c8 · snapshot:pre-deploy-kkb-hi-in-2026-07-27_022433 · deployed
2026-07-27 02:24:33 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:46e12c33 · snapshot:pre-deploy-kkb-kn-in-2026-07-27_022433 · deployed
2026-07-27 02:31:39 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e68d7622 · snapshot:pre-deploy-maya-hi-out-2026-07-27_023139 · deployed
2026-07-27 02:31:39 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:68f5224e · snapshot:pre-deploy-maya-hi-in-2026-07-27_023139 · deployed
2026-07-27 02:31:40 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:08c7b4c6 · snapshot:pre-deploy-kkb-hi-out-2026-07-27_023140 · deployed
2026-07-27 02:31:40 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:3b8cf2bc · snapshot:pre-deploy-kkb-kn-out-2026-07-27_023140 · deployed
2026-07-27 02:31:41 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:5ed86a87 · snapshot:pre-deploy-kkb-hi-in-2026-07-27_023140 · deployed
2026-07-27 02:31:41 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:a8d5170b · snapshot:pre-deploy-kkb-kn-in-2026-07-27_023141 · deployed
2026-07-27 12:16:33 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:62967128 · snapshot:- · dry-run
2026-07-27 12:16:41 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:62967128 · snapshot:pre-deploy-kkb-hi-in-2026-07-27_121640 · deployed
2026-07-27 12:16:41 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:e1a58e0a · snapshot:pre-deploy-kkb-kn-in-2026-07-27_121641 · deployed
2026-07-27 14:00:45 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:3fda09a9 · snapshot:pre-deploy-maya-hi-in-2026-07-27_140044 · deployed
2026-07-27 14:00:45 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:79f48c0e · snapshot:pre-deploy-kkb-hi-in-2026-07-27_140045 · deployed
2026-07-27 14:00:46 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:74b89498 · snapshot:pre-deploy-kkb-kn-in-2026-07-27_140045 · deployed
2026-07-27 14:00:46 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:71019e54 · snapshot:pre-deploy-kkb-hi-out-2026-07-27_140046 · deployed
2026-07-27 14:00:46 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:150433f1 · snapshot:pre-deploy-kkb-kn-out-2026-07-27_140046 · deployed
2026-07-27 14:00:47 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:d82f163c · snapshot:pre-deploy-maya-hi-out-2026-07-27_140047 · deployed
2026-07-27 15:00:50 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:1600f0a5 · snapshot:pre-deploy-kkb-kn-signals-2026-07-27_150049 · deployed
2026-07-27 15:02:01 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:1a442549 · snapshot:pre-deploy-kkb-kn-signals-2026-07-27_150201 · deployed
2026-07-27 15:43:58 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:c1e80d67 · snapshot:pre-deploy-kkb-kn-signals-2026-07-27_154358 · deployed
2026-07-27 16:06:45 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:614e7c61 · snapshot:pre-deploy-kkb-hi-out-2026-07-27_160645 · deployed
2026-07-27 16:06:46 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:2944cf61 · snapshot:pre-deploy-kkb-kn-out-2026-07-27_160645 · deployed
2026-07-27 16:50:56 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:7be0fe89 · snapshot:pre-deploy-kkb-kn-signals-2026-07-27_165056 · deployed
2026-07-29 15:26:26 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:9d63073a · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_152625 · deployed
2026-07-29 15:48:42 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:f48ae8bb · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_154842 · deployed
2026-07-29 16:02:03 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:6db42235 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_160203 · deployed
2026-07-29 16:37:27 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:4f730d45 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_163727 · deployed
2026-07-29 16:59:54 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:087e7f50 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_165954 · deployed
2026-07-29 17:07:25 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:d9fe6d82 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_170725 · deployed
2026-07-29 17:16:56 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:6da03377 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_171656 · deployed
2026-07-29 18:48:37 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:81bda6be · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_184837 · deployed
2026-07-29 20:05:07 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:75466c7f · snapshot:pre-deploy-kkb-hi-signals-2026-07-29_200506 · deployed
2026-07-29 21:12:22 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:a155cb82 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_211221 · deployed
2026-07-29 21:19:37 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:9296eb64 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_211937 · deployed
2026-07-29 21:19:38 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:d7a7600f · snapshot:pre-deploy-kkb-hi-signals-2026-07-29_211937 · deployed
2026-07-29 21:45:52 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:c93c8df3 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_214552 · deployed
2026-07-29 21:45:52 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:efd79e0c · snapshot:pre-deploy-kkb-hi-signals-2026-07-29_214552 · deployed
