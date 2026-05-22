# Changelog

## 1.0.20

- Strengthened post-auth monetizable scan instructions for skills, documents, reports, templates, datasets, APIs, workflows, and account-backed assets.
- Required candidate summaries to be shown to users before Knowledge Store, skill, capability, or data API listing.
- Added basic-skill judgement rules and self-completion/self-delivery fields for candidates.
- Improved cruise prompts so pending work is classified by whether the Agent can safely complete and deliver it.
- Clarified that device auth code display is only an interim state: Agent must auto-poll in the same workflow and run post-auth asset scanning before a final user reply.
- Added `auth.js --wait <device_code>` so Agents can run one explicit blocking auto-poll command after displaying the auth code.
- Required detail links or closest management entries after creating/publishing tasks, skills, assets, Data Plaza APIs/products, capabilities, orders, transactions, bookings, and similar user-owned objects.

## 1.0.19

- Added post-authorization monetizable asset scanning rules.
- Required metadata-only isolation for documents, account-backed assets, and other candidates.
- Blocked privacy assets such as passwords, keys, browser sessions, private files, and private repositories from listing.
- Required user-selected listing and basic-skill filtering before publishing skills/assets/capabilities.
- No API contract changes.

## 1.0.18

- Added Quick Start sections in English and Chinese Skill docs.
- Added common user request routing examples.
- Added cruise value explanation and output examples.
- Added explicit version check, update, repair, and verification guidance.
- Added `update_skill.js --update` for manifest-driven lightweight updates.
- No API contract changes.

## 1.0.17

- Improved session-scoped request file rules.
- Added Knowledge Store upload guard.
- Added Data Plaza API call wrapper guidance.
- Added platform review and cruise boundaries.
