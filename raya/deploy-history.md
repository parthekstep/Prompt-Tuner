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
