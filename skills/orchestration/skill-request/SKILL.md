---
name: skill-request
description: >-
  Offer to contribute back to the ai-security-skills project by opening a public GitHub issue that asks for
  a new skill, when an assessment finds systems that no skill covers. Use at the end of a full assessment
  that found "no skill" systems, or when the user asks to request a skill for a product.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "Any assessment run with this collection"
  audience: "home, work, homelab"
  finding_prefix: "REQ"
  modes: "discover"
---

# Skill Request (Contribute Back)

When an assessment finds systems that no skill in this collection covers, offer the user a simple way to
help: a public GitHub issue on the project asking for a skill for that kind of product. This skill makes
sure the user stays in control and that nothing about their own environment ends up in a public issue.

## How to use this skill

The [full-assessment](../full-assessment/SKILL.md) skill calls this at the end of a run that found systems
with `coverage: no_skill`. The user can also ask for it directly ("request a skill for my robot mower").
The core [operating principles](../../../core/operating-principles.md) apply, and so do the project's
content rules, which come down to the "Rules" below.

Project issues: https://github.com/kireol/ai-security-skills/issues

## Rules

- **Ask first, every time.** Opening an issue publishes text on the internet under the user's GitHub
  account. Never create one without the user's explicit approval of the exact text, product by product.
  A "no" or no answer means no issue.
- **Describe the product, never the setup.** The issue may contain only: the product's make and product
  family, its general category, why it matters in general terms, vendor-default ways to recognize it
  (default ports, page titles, discovery announcements), and links to the vendor's public documentation.
- **Never include:** hostnames, IP or MAC addresses, serial numbers, exact firmware builds, account or
  user names, room or location names, network layout, screenshots, findings or evidence from the run,
  anything copied from the run folder, or anything that identifies the user or their household.
- **One issue per product type,** and only after checking that no open or closed issue already asks for it.
- **The user submits.** Prefer a pre-filled link the user opens and submits themselves. Create the issue
  from the command line only if the user asks you to and the GitHub CLI is already signed in.

## Steps

1. **List the candidates.** From the run's inventory, collect systems with `coverage: no_skill` and group
   them by product type (five identical smart plugs are one request). Leave out anything the user marked
   out of scope.
2. **Ask.** Show the list and explain in one or two sentences: "These have no dedicated skill yet. I can
   draft a public GitHub issue asking the project for one; it would describe only the product, nothing
   about your network. Want me to draft any of them?" Let the user pick.
3. **Check for duplicates.** Search the project's issues for each product (with the GitHub CLI:
   `gh issue list --repo kireol/ai-security-skills --state all --search "<product> in:title"`; otherwise
   give the user a search link:
   `https://github.com/kireol/ai-security-skills/issues?q=<product>`). If one exists, offer to show it
   instead of drafting a new one (the user can add a thumbs-up there).
4. **Draft.** Fill in the fields of the project's skill-request form:

   | Field | Content |
   |---|---|
   | Title | `Skill request: <make and product family>` |
   | Product | Make and product family |
   | Category | One of the form's categories |
   | Why it matters | What the product does and what could go wrong, in general terms |
   | How to recognize it | Vendor-default ports, page titles, or discovery announcements, if known |
   | Vendor documentation | Links to the vendor's public security or support pages, if known |

   Then check the draft against the rules above. If this collection's `scripts/check-content.sh` is
   available, save the draft to a temporary file outside the run folder and run the script on it; remove
   anything it flags.
5. **Show the full text and ask for approval.** Show exactly what will be published. Make changes the user
   asks for, and show it again. Proceed only on a clear "yes".
6. **Submit.** Either:
   - **Pre-filled link (preferred):** build a link to the form with each field URL-encoded, for example
     `https://github.com/kireol/ai-security-skills/issues/new?template=skill-request.yml&title=<title>&product=<product>&why=<why>&detection=<detection>&references=<links>`,
     and give it to the user to open, review, tick the privacy box, and submit; or
   - **GitHub CLI (only if the user asks and `gh` is already signed in):** create it with
     `gh issue create --repo kireol/ai-security-skills --title "<title>" --body-file <draft file>`, with
     the body laid out under the same headings as the form, ending with the privacy statement. Then
     delete the draft file.
7. **Report back** the issue link (or that the user will submit it), and thank them.

## Example (invented)

> **Skill request: Example Brand robot lawn mower (2nd generation)**
>
> **Category:** home automation / smart home
>
> **Why it matters:** App- and cloud-controlled outdoor device with a camera, GPS, and anti-theft PIN.
> An insecure account or local API could reveal the property layout or let someone disable the
> anti-theft lock.
>
> **How to recognize it:** Announces itself over mDNS with the vendor's name; the vendor documents a
> local status page on port 80.
>
> **Vendor documentation:** <vendor support and security links>
>
> This issue contains no details from my own network, devices, or accounts.

## Version history

- **1.0** (2026-10-30): Initial version.
