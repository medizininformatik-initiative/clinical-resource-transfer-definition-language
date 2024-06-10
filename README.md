# CRTDL 

**C**linical **R**esource **T**ransfer **D**efinition **L**anguage

## Description
This repo contains schema and example JSON files describing the Clinical Resource Transfer Definition Language (**CRTDL**) for the FDPG+ framework used to extract medical data based on specific criteria defined in a cohort. The query provides a what data to extract from a defined cohort. 

## Purpose

The DEQ is utilized to describe data extraction inside the FDPG+ infrastructure. 
**TBD**:more desc. 


## Structure

A DEQ consists of 2 Parts:
The cohort definition in **CCDL**, see [**CCDL specs**](https://github.com/medizininformatik-initiative/clinical-cohort-definition-language/tree/main) for further details and a data extraction object.

The data extraction object contains an array defining **attributeGroups**, which bundle attributes together.

Each group has an identifier for the group called **groupReference**, a list of attributes to be extracted **attributes** and a filter object containing a time filter **** and a  list of code filters **filters**.

An attributes to be extracted contains an attribute reference **attributeRef** and information if the attribute is required **must-have** e.g. ``` {
            "attributeRef": "medicationCode",
            "mustHave": true
          }```. 


If a **must have** condition is **violated**, it will result in a complete stop of the extraction for a **patient**. 

Filters definition have a list of **FHIR search parameter operations** containing the type supported, name and corresponding parameters. Currrently **token** and **date** are supported.  

## Example

Here is a example of a CRTDL JSON:

```json
{
    "version": "http://json-schema.org/to-be-done/schema#",
    "display": "",
    "cohortDefinition": {
      "version": "http://to_be_decided.com/draft-1/schema#",
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

      ],
        "dataExtraction": {
          "attributeGroups": [
            {
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
}

```
# Whitelisting

Whitelisting happens at data integration center (DIC) level.  

## Structure

The Structure is equivalent to the **CRTDL** attributeGroups. Group references are FHIR compliant e.g. **profiles/ressources**. 

## Example

```
{
  "version": "whitelist1.0",
  "dataExtraction": {
    "attributeGroups": [
      {
        "groupReference": "https://www.medizininformatik-initiative.de/fhir/core/modul-fall/StructureDefinition/KontaktGesundheitseinrichtung",
        "attributes": [
          {
            "attributeRef": "Encounter.diagnosis"
          }
        ]
      }
    ]
  }
}

```