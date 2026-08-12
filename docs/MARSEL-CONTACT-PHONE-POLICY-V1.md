# MARSEL — Contact Phone Policy V1

Status: DESIGN / NOT LIVE IN RO APP

## Canonical phone category
MARSEL uses exactly one phone category:

`mobile` — `Мобильный`

No separate categories for home, work, fax or other phone types are part of the MARSEL reference model.

## Normalization
A phone number must be normalized to a canonical representation before duplicate detection or synchronization. The normalization implementation must preserve the actual country/number information and must not silently alter a number when validation fails.

## Validation
Before accepting a number:
- reject empty/invalid values;
- validate the normalized telephone structure;
- preserve the original user-entered value separately if audit requirements require it;
- detect duplicates after normalization;
- do not infer ownership of a number from external sources.

## Multiple mobile numbers
A customer may have more than one mobile number when the business process requires it. Every number still has the same category: `Мобильный`.

## Deduplication
Duplicate detection must use the normalized number, not formatting differences such as spaces, brackets or separators.

## Scope
Apply the same canonical category to customers, employees and contact persons wherever a phone field is used in the MARSEL model.

## Ro App mapping
This is the MARSEL canonical policy. Actual Ro App field names, enum values and supported cardinality must be verified against the live schema before synchronization or production writes.

## Safety
This policy changes the project specification only. It does not modify live Ro App data.
