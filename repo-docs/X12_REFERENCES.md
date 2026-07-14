# X12 / EDI Reference Material

External references for looking up ASC X12 segments, data elements, and code-table
values when working on this library — for example, when adding a transaction (see
[NEW_TRANSACTION.md](./NEW_TRANSACTION.md)) or extending a code-table `Enum` in a
`segments.py` module.

> The data-model `Enum` classes in `segments.py` (e.g. a DTP `DateTimeQualifier`)
> map directly to X12 **data element** code tables. When a real-world message uses a
> code the model rejects, confirm the code's meaning in one of the references below
> before adding it, and note whether it is in-scope for the relevant HIPAA
> implementation guide (TR3) or a permissible real-world extension.

## General lookups (segments, elements, codes)

- **Stedi EDI Reference** — https://www.stedi.com/edi/x12
  Browsable, version-aware catalog of every X12 segment, data element, and the full
  code list for each element. Best first stop for "what does code _N_ mean?".
  Example: Date/Time Qualifier (element 374) — https://www.stedi.com/edi/x12/element/374
- **Zenbridge EDI Dictionary** — https://zenbridge.io/edi-dictionary/X12/
  Version-specific (4010, 5010, 7010, …) browser for segments, elements, and codes.
- **ASC X12 (official standards body)** — https://x12.org/
  Authoritative source for the standard itself and the transaction set catalog
  (https://x12.org/products/transaction-sets). The normative definitions live here.

## Healthcare implementation guides (HIPAA TR3s)

The healthcare transactions this library parses are governed by ASC X12N
**Technical Report Type 3 (TR3)** implementation guides, which constrain the base
standard (allowed loops, segments, and code values per context). They are the
authority for which codes are valid *in a given loop*. The transactions supported
here and their guide identifiers:

| Transaction | Implementation guide | Module |
| ----------- | -------------------- | ------ |
| 270 / 271 Eligibility Inquiry / Response | 005010X279A1 | `v5010/x12_270_005010X279A1`, `v5010/x12_271_005010X279A1` |
| 276 / 277 Claim Status Request / Response | 005010X212 | `v5010/x12_276_005010X212`, `v5010/x12_277_005010X212` |
| 834 Benefit Enrollment & Maintenance | 005010X220A1 | `v5010/x12_834_005010X220A1` |
| 835 Claim Payment / Advice | 005010X221A1 | `v5010/x12_835_005010X221A1` |
| 837 Professional Claim | 005010X222A2 | `v5010/x12_837_005010X222A2` |
| 837 Institutional Claim | 005010X223A3 | `v5010/x12_837_005010X223A3` |
| 837 Professional / Institutional (legacy 4010) | 004010X098A1 / 004010X096A1 | `v4010/...` |

TR3 guides are published/licensed through ASC X12 (https://x12.org/products) and were
historically distributed via the Washington Publishing Company (WPC). Many payers also
publish free **companion guides** that summarize the loop/segment/code constraints they
accept in practice — useful when a production message deviates from the base TR3.

## See also

- **EDI Academy — X12 Date/Time Qualifiers** — https://ediacademy.com/blog/x12-date-time-qualifiers/
  Convenient quick-reference for element 374 codes (occasionally rate-limited).

---

_These links are external and may change. The normative source is always the ASC X12
standard and the applicable TR3 implementation guide; the third-party references above
are convenient, generally-accurate lookups._
