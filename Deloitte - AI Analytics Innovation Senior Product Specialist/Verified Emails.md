# Verified Emails — Deloitte AI & Analytics Innovation Senior Product Specialist

Recipient addresses for the `write-outreach` Gmail-draft step. The skill reads this table and matches the contact name (case-insensitive) to fill the To: field. **Only mark an address `verified` once you've actually confirmed it** — everything starts `unverified` and may bounce. Deloitte uses at least three email patterns, so guesses are genuinely uncertain.

| Name | Email | Confidence |
|------|-------|------------|
| Wendy Warne | wwarne@deloitte.com | unverified |
| Gina Stewart | gstewart@deloitte.com | unverified |
| Allison Brown | abrown@deloitte.com | unverified |
| Matthew Lee | mlee@deloitte.com | unverified |
| Akash Shukla | ashukla@deloitte.com | unverified |
| Sourjya Guha | sguha@deloitte.com | unverified |
| Maggie Kotek | mkotek@deloitte.com | unverified |
| Nara-Jayne Linéus | nlineus@deloitte.ca | unverified |

**Notes**
- `verified` = you confirmed it (delivery, reply, or a trusted source). `unverified` = inferred guess; verify before sending.
- The `write-outreach` skill falls back to madhok.kanu@gmail.com (with a gap flag) if a contact isn't found here — so a typo'd name silently routes to yourself, not the contact. Match the name spelling the skill will pass.
