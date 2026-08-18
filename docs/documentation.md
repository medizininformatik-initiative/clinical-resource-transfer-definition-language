---
aside: true
outline: [2, 3]
---

# Clinical Resource Transfer Definition Language (CRTDL)

This repo contains schema and example JSON files describing the Clinical Resource Transfer Definition Language (**CRTDL**) used to extract medical data based on specific criteria defined in a cohort. The query provides what data to extract from a defined cohort.

## Purpose

The CRTDL is used to formally describe data extraction for clinical Data Use Project Data Extractions.

## Structure

A CRTDL consists of 2 Parts:

### The cohort definition 

The `cohortDefinition` part is defined in **CCDL**, see the [CCDL documentation](https://medizininformatik-initiative.github.io/clinical-cohort-definition-language/) for further details.

This part selects the `who` the data is extracted for - the cohort.

### The data extraction definition

The `dataExtraction` part defines the `what` data should be extracted for the cohort defined in the first part - the features/variables.

It holds an array defining **attributeGroups**, which bundle attributes together.

Each group has a unique **id**, a **groupReference** pointing at the FHIR StructureDefinition the group targets, a list of attributes to be extracted **attributes**, and an optional filter object containing a time filter and a list of code filters, see [Filters](#filters).

Each group also has a human-readable **name** (required, 1-64 characters, no leading/trailing whitespace) that is shown to users and, via [slugification](#slugification), determines the [output file name](#output-file-names) used when flattening extracted data. **name** must be [unique](#uniqueness-comparison) across all `attributeGroups` in the CRTDL after slugification.

### Slugification of attributeGroup names

Slugification turns a free-text **name** of an `attributeGroup` into a normalized, file-system- and URL-safe token by applying the following steps, in order:

1. Trim leading and trailing whitespace.
2. Convert to lowercase.
3. Transliterate German-specific characters to their conventional ASCII spelling: `ä` → `ae`, `ö` → `oe`, `ü` → `ue`, `ß` → `ss`.
4. Normalize to Unicode NFKD form and drop combining diacritical marks (Unicode category Mn), folding any other accented Latin letter to its base letter (e.g. `é` → `e`, `ñ` → `n`, `ç` → `c`).
5. Replace every run of one or more characters outside `a-z` and `0-9` with a single `_` (underscore).
6. Strip any leading or trailing `_`.

For example, `"Hemoglobin Observation"` slugifies to `hemoglobin_observation`, and `"Typhus Diagnosis"` slugifies to `typhus_diagnosis`. [Output file names](#output-file-names) and the [uniqueness comparison](#uniqueness-comparison) both build on this algorithm.

Step 3 exists because German names are common in this format: folding `ä`/`ö`/`ü`/`ß` to `ae`/`oe`/`ue`/`ss` keeps the slug readable and matches everyday German transliteration, instead of letting them fall through to step 5 and collapse into a bare separator. Step 4 is a general fallback for other Latin-script accents that step 3 doesn't cover. For example, `"Meine Hämoglobin Werte von 2020!"` slugifies to `meine_haemoglobin_werte_von_2020`: `ä` becomes `ae` in step 3 before the separator-collapsing step ever sees it, each space becomes a `_`, and the trailing `!` is dropped as a trailing separator.

### Output file names

The base file name used for an attribute group's flattened output is the [slugified](#slugification) form of its **name**.

### Uniqueness comparison

**name** of `attributeGroups` must be unique within a CRTDL's `attributeGroups`, but uniqueness is evaluated on the [slugified](#slugification) form, not the raw string. Two names that differ only in case, whitespace, or punctuation collapse to the same slug and therefore count as a duplicate — for example, `"Hemoglobin Observation"` and `"hemoglobin  observation!"` both slugify to `hemoglobin_observation` and must not appear together in the same CRTDL. Consuming tooling must slugify every attribute group's **name** and reject the CRTDL if any two slugs are equal.

### Consent Handling

Consent rules can be embedded directly in the cohort definition as `inclusionCriteria` entries with `context.code = "Einwilligung"`. Extraction tooling that supports consent enforcement (such as [TORCH](https://medizininformatik-initiative.github.io/torch/)) filters resources against each patient's consent window using these entries — resources outside the window are excluded. If no `Einwilligung` entries are present, consent enforcement is skipped and all resources are treated as consented.

Each consent code is an MII OID provision code listed under a `context.code = "Einwilligung"` criterion in `inclusionCriteria`. For example, FDPG Zentrale Analyse requires both `MDAT wissenschaftlich nutzen` (`.8`, validity gate) and `MDAT erheben` (`.6`, data-extraction window):

```json
{
  "inclusionCriteria": [
    [
      {
        "context": {
          "code": "Einwilligung",
          "display": "Einwilligung",
          "system": "fdpg.mii.cds",
          "version": "1.0.0"
        },
        "termCodes": [
          {
            "code": "2.16.840.1.113883.3.1937.777.24.5.3.8",
            "display": "MDAT wissenschaftlich nutzen EU DSGVO NIVEAU",
            "system": "urn:oid:2.16.840.1.113883.3.1937.777.24.5.3",
            "version": "1.0.7"
          }
        ]
      }
    ],
    [
      {
        "context": {
          "code": "Einwilligung",
          "display": "Einwilligung",
          "system": "fdpg.mii.cds",
          "version": "1.0.0"
        },
        "termCodes": [
          {
            "code": "2.16.840.1.113883.3.1937.777.24.5.3.6",
            "display": "MDAT erheben",
            "system": "urn:oid:2.16.840.1.113883.3.1937.777.24.5.3",
            "version": "1.0.7"
          }
        ]
      }
    ]
  ]
}
```

### Attributes and Must-Have

An attribute to be extracted contains an attribute reference **attributeRef** and a flag indicating whether the attribute is required, **mustHave**, e.g.:

```json
{
  "attributeRef": "medicationCode",
  "mustHave": true
}
```

When `mustHave: true` is set on at least one attribute in a group, extraction tooling enforces that every patient has at least one resource of that group where all `mustHave: true` attributes are populated; patients for whom no such resource exists are dropped from the extraction result entirely. When no attribute in a group carries `mustHave: true`, the group is optional — patients are retained even if they have no resources for that group.

Standard attributes such as `id`, `meta.profile`, and patient-compartment references (e.g. `subject`) are generally enforced independently of `mustHave` by extraction tooling and are not subject to `mustHave` filtering themselves.

### Linked and Reference-Only Groups

An attribute can carry **linkedGroups**, an array of other attribute group `id`s it references. This lets one group pull in resources resolved through another group's reference — for example, a diagnosis group linking to an encounter group via `Condition.encounter`.

A group can be marked **includeReferenceOnly**, meaning it is only extracted when linked to from another group's attribute rather than independently. See [`CRTDL_Diagnosis_linked_with_Encounter.json`](https://github.com/medizininformatik-initiative/clinical-resource-transfer-definition-language/blob/main/example-json/CRTDL_Diagnosis_linked_with_Encounter.json) for a full example:

```json
{
  "id": "0cb4bbf1-3c2c-4549-b738-d005130257fb",
  "name": "Typhus Diagnosis",
  "groupReference": "https://www.medizininformatik-initiative.de/fhir/core/modul-diagnose/StructureDefinition/Diagnose",
  "attributes": [
    {
      "attributeRef": "Condition.encounter",
      "mustHave": true,
      "linkedGroups": ["f15dc0a3-9076-4fb6-8703-7c74bb6efea0"]
    }
  ]
},
{
  "id": "f15dc0a3-9076-4fb6-8703-7c74bb6efea0",
  "name": "Typhus Encounter",
  "includeReferenceOnly": true,
  "groupReference": "https://www.medizininformatik-initiative.de/fhir/core/modul-fall/StructureDefinition/KontaktGesundheitseinrichtung",
  "attributes": [
    { "attributeRef": "Encounter.hospitalization", "mustHave": true }
  ]
}
```

## Filters

Each attribute group's **filter** array holds FHIR search parameter operations. The `name` field corresponds to the `code` field of a FHIR SearchParameter, which identifies how the filter should be applied. Currently **token** and **date** are supported.

### Token Filter

Token filters restrict resources to a set of specific codes or identifiers, such as LOINC or SNOMED CT codes, via a **codes** array:

```json
{
  "type": "token",
  "name": "code",
  "codes": [
    {
      "code": "718-7",
      "system": "http://loinc.org",
      "display": "Hemoglobin [Mass/volume] in Blood"
    }
  ]
}
```

### Date Filter

Date filters restrict resources to a date range via **start** and **end** (day-wise granularity):

```json
{
  "type": "date",
  "name": "date",
  "start": "2021-09-09",
  "end": "2021-10-09"
}
```

## Validation

The JSON Schema alone cannot express every constraint a valid CRTDL must satisfy. Validators (and any tooling that consumes a CRTDL directly) must additionally check:

- **Attribute group `id`s are unique** within a CRTDL document. A duplicate `id` makes every `linkedGroups` reference to that `id` ambiguous.
- **Attribute group `name`s are unique after [slugification](#slugification)** within a CRTDL document (see [Uniqueness comparison](#uniqueness-comparison)). Tooling that derives one output artifact per group from its slugified `name` (for example, one CSV file per group when flattening) silently loses data if two groups' names collapse to the same slug.
- **Every `linkedGroups` entry resolves.** Each value in `attributes[].linkedGroups` must equal the `id` of an attribute group present in the same document.
- **In a `date` filter, `end` must not be before `start`.** A reversed range selects nothing and is usually an authoring error.
- **The [slugified](#slugification) form of `name` is not a Windows reserved device name.** `con`, `prn`, `aux`, `nul`, `com1`–`com9`, and `lpt1`–`lpt9` are rejected, since the slug becomes the base name of an output file when flattening extracted data. Because slugification lowercases and strips punctuation, this also rejects names like `"Con!"` or `"CON"`, not just an exact, literal `"con"`.

### Format assertion

JSON Schema draft 2020-12 treats `format` (e.g. `uri`, `date`) as an annotation by default — a validator only rejects malformed values if format assertion is explicitly enabled. Validators for CRTDL documents must enable format assertion rather than relying on `format` as an annotation only, otherwise fields like `groupReference` or a filter's `start`/`end` accept syntactically invalid values.

### Reference validator

[`scripts/validate_crtdl.py`](https://github.com/medizininformatik-initiative/clinical-resource-transfer-definition-language/blob/main/scripts/validate_crtdl.py) implements this section: it validates a CRTDL document against the JSON Schema with format assertion enabled, then applies the rules above. Install dependencies with `pip install -r requirements.txt` and run:

```sh
python scripts/validate_crtdl.py example-json/*.json
```

By default it resolves the `cohortDefinition` schema from the published CCDL repository; pass `--ccdl-schema <path>` to validate against a local checkout instead.

[`example-json/invalid/`](https://github.com/medizininformatik-initiative/clinical-resource-transfer-definition-language/tree/main/example-json/invalid) holds documents that deliberately violate these rules, one violation per attribute group (labeled in each group's `id`), so running the validator against them demonstrates every check above:

```sh
python scripts/validate_crtdl.py example-json/invalid/*.json
```

These are intentionally excluded from `example-json/*.json` so they aren't mistaken for valid examples.

## Example

Here is an example of a CRTDL JSON:

```json
{
    "version": "1",
    "display": "",
    "cohortDefinition": {
      "version": "2",
      "display": "",
      "inclusionCriteria": [
        [
            {
              "termCodes": [
                {
                  "code": "424144002",
                  "system": "http://snomed.info/sct",
                  "display": "Gegenwärtiges chronologisches Alter"
                }
              ],
              "context": {
                "code": "Patient",
                "system": "fdpg.mii.cds",
                "version": "1.0.0",
                "display": "Patient"
              },
              "valueFilter": {
                "type": "quantity-comparator",
                "unit": {
                  "code": "a",
                  "display": "a"
                },
                "value": 18,
                "comparator": "gt"
              }
            }
          ],
          [
            {
              "termCodes": [
                {
                  "code": "263495000",
                  "system": "http://snomed.info/sct",
                  "display": "Geschlecht"
                }
              ],
              "context": {
                "code": "Patient",
                "system": "fdpg.mii.cds",
                "version": "1.0.0",
                "display": "Patient"
              },
              "valueFilter": {
                "selectedConcepts": [
                  {
                    "code": "female",
                    "display": "Female",
                    "system": "http://hl7.org/fhir/administrative-gender"
                  }
                ],
                "type": "concept"
              }
            }
          ],
          [
            {
              "termCodes": [
                {
                  "code": "8-918",
                  "system": "http://fhir.de/CodeSystem/bfarm/ops",
                  "version": "2023",
                  "display": "Interdisziplinäre multimodale Schmerztherapie"
                }
              ],
              "context": {
                "code": "Procedure",
                "system": "fdpg.mii.cds",
                "version": "1.0.0",
                "display": "Prozedur"
              }
            }
          ]

      ]
    },
    "dataExtraction": {
      "attributeGroups": [
        {
          "id": "be963395-3186-4ae6-8a23-18968bcb8857",
          "name": "Hemoglobin Observation",
          "groupReference": "https://www.medizininformatik-initiative.de/fhir/core/modul-labor/StructureDefinition/ObservationLab",
          "attributes": [
            {
              "attributeRef": "Observation.code",
              "mustHave": false
            },
            {
              "attributeRef": "Observation.value",
              "mustHave": true
            }
          ],
          "filter": [
            {
              "type": "token",
              "name": "code",
              "codes": [
                {
                  "code": "718-7",
                  "system": "http://loinc.org",
                  "display": "Hemoglobin [Mass/volume] in Blood"
                },
                {
                  "code": "33509-1",
                  "system": "http://loinc.org",
                  "display": "Hemoglobin [Mass/volume] in Body fluid"
                }
              ]
            },
            {
              "type": "date",
              "name": "date",
              "start": "2021-09-09",
              "end": "2021-10-09"
            }
          ]
        }
      ]
    }
}
```

## Schema and Examples

Schema: [CRTDL_schema.json](https://github.com/medizininformatik-initiative/clinical-resource-transfer-definition-language/blob/main/json-schema/CRTDL_schema.json)

Examples:
- [CRTDL_observation.json](https://github.com/medizininformatik-initiative/clinical-resource-transfer-definition-language/blob/main/example-json/CRTDL_observation.json)
- [CRTDL_diagnosis.json](https://github.com/medizininformatik-initiative/clinical-resource-transfer-definition-language/blob/main/example-json/CRTDL_diagnosis.json)
- [CRTDL_Diagnosis_linked_with_Encounter.json](https://github.com/medizininformatik-initiative/clinical-resource-transfer-definition-language/blob/main/example-json/CRTDL_Diagnosis_linked_with_Encounter.json)
