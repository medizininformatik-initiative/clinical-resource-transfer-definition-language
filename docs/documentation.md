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

Each group also has a machine-readable **name** (required, unique within the CRTDL, matching `^[a-z0-9]([a-z0-9_]*[a-z0-9])?$`, max 100 chars) that consumers use verbatim as the base file name when flattening extracted data, and an optional human-readable **display** label shown to users. **name** is not meant for display, and **display** is not constrained or required to be unique.

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
  "name": "typhus_diagnosis",
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
  "name": "typhus_encounter",
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

## Example

Here is an example of a CRTDL JSON:

```json
{
    "version": "1.0.0",
    "display": "",
    "cohortDefinition": {
      "version": "2.0.0",
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
          "name": "hemoglobin_observation",
          "display": "Hemoglobin Observation",
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
