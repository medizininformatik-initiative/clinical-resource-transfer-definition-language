# DEQ

Schema and example JSON files describing the Data Extraction Query (**DEQ**) for the FDPG+ framework used to extract medical data based on specific criteria defined in a cohort. The query provides a what data to extract from a defined cohort. 

## Purpose

The DEQ is utilized to describe data extraction inside the FDPG+ infrastructure. 
**TBD**:more desc. 


## Structure

A DEQ consists of 2 Parts:
The cohort definition in **CCDL**, see [**CCDL specs**](https://github.com/medizininformatik-initiative/clinical-cohort-definition-language/tree/main) for further details and a data extraction object.

The data extraction object contains an array defining **attributeGroups**, which bundle attributes together.

Each group has an identifier for the group called **groupReference**, a list of attributes to be extracted **attributes** and list of filters **filters**.

An attributes to be extracted contains an attribute reference *attributeRef* and information if the attribute is required **must-have** e.g. ``` {
            "attributeRef": "medicationCode",
            "mustHave": true
          }```. 


If a **must have** condition is **violated**, it will result in a complete stop of the extraction for a **patient**. 

Filters definition is equivalent to the filter definition in **CCDL**.

## Example

Here is a example of a DEQ JSON:

```json
{
  "version": "http://to_be_decided.com/draft-1/schema#",
  "display": "Data Extraction for Cardiovascular Study",
  "cohortDefinition": {
    "version": "http://to_be_decided.com/draft-1/schema#",
    "display": "Cardiovascular Disease Patients 18+",
    "inclusionCriteria": [
      [
        {
          "termCodes": [
            {
              "code": "424144002",
              "system": "http://snomed.info/sct",
              "display": "Current chronological age"
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
              "display": "years"
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
              "code": "53741008",
              "system": "http://snomed.info/sct",
              "display": "Coronary artery disease"
            }
          ],
          "context": {
            "code": "Diagnosis",
            "system": "fdpg.mii.cds",
            "version": "1.0.0",
            "display": "Diagnosis"
          }
        }
      ]
    ],
    "exclusionCriteria": [
      [
        {
          "termCodes": [
            {
              "code": "38341003",
              "system": "http://snomed.info/sct",
              "display": "Hypertension"
            }
          ],
          "context": {
            "code": "Condition",
            "system": "fdpg.mii.cds",
            "version": "1.0.0",
            "display": "Condition"
          }
        }
      ]
    ]
  },
  "dataExtraction": {
    "attributeGroups": [
      {
        "groupReference": "MedicationDetails",
        "attributes": [
          {
            "attributeRef": "medicationCode",
            "mustHave": true
          },
          {
            "attributeRef": "dosage",
            "mustHave": true
          }
        ],
        "filter": [
          [
            {
              "termCodes": [
                {
                  "code": "B01",
                  "system": "http://fhir.de/CodeSystem/bfarm/atc",
                  "version": "2022",
                  "display": "Antithrombotic Agents"
                }
              ],
              "context": {
                "code": "Medication",
                "system": "fdpg.mii.cds",
                "version": "1.0.0",
                "display": "Medication administered"
              }
            }
          ]
        ]
      }
    ]
  }
}

```
