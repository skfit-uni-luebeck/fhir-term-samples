import sqlite3
from get_session import FhirApi
import get_session
from fhir.resources.valueset import ValueSet, ValueSetCompose, ValueSetComposeInclude, ValueSetComposeIncludeConcept
from fhir.resources.codesystem import CodeSystem, CodeSystemConcept, CodeSystemConceptProperty, CodeSystemProperty
from fhir.resources.conceptmap import ConceptMap
from fhir.resources.parameters import Parameters
from fhir.resources.bundle import Bundle
from rich import print, inspect
import questionary
import urllib.parse
from questionary import Validator, ValidationError
from typing import List, Dict
import json

class NotEmptyValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Please enter a value",
                cursor_position=len(document.text),
            )

fhir_api = FhirApi(endpoint="https://r4.ontoserver.csiro.au/fhir", cert_file=None)
sql = "SELECT code, display, unit, loinc FROM lab_codes;"
sqlconn = sqlite3.connect("../legacydb.sqlite3")
sqlconn.row_factory = sqlite3.Row # access rows using Row interface, instead of tuples
cur = sqlconn.cursor()
# list the available concepts from the DB as list of dict
defined_concepts : List[Dict[str, str]] = []
for row in cur.execute(sql):
    defined_concepts.append(dict(zip(row.keys(), row)))
print(defined_concepts)

# query for attributes of the FHIR CodeSystem
cs_answers = questionary.form(
    url = questionary.text("Canonical URL of the CodeSystem?", validate=NotEmptyValidator),
    valueSet = questionary.text("Canonical URL of the ValueSet?", validate=NotEmptyValidator),
    version = questionary.text("Version?", validate=NotEmptyValidator),
    title = questionary.text("Title (for humans)?", validate=NotEmptyValidator),
    name = questionary.text("Name (for machines), and id?", validate=NotEmptyValidator),
    status = questionary.select("Status", choices=["draft", "active", "retired", "unknown"])
).ask()

cs_answers.update({
    "id": cs_answers["name"],
    "content": "complete",
    })

code_system = CodeSystem(**cs_answers)

code_system.property = [CodeSystemProperty(**{"code": "unit", "type": "string"})]
code_system.concept = [CodeSystemConcept(**{
    "code": c["code"],
    "display": c["display"],
    "property": [CodeSystemConceptProperty(**{
        "code": "unit",
        "valueString": c["unit"]
        })]
    }) for c in defined_concepts]
print(code_system.json())
with open("codesystem.fhir.json", "w") as jf:
    json.dump(json.loads(code_system.json()), jf, indent=2)
    print("Wrote CodeSystem to codesystem.fhir.json")

# query for attributes of the FHIR ValueSet for LOINC
vs_answers = questionary.form(
    url = questionary.text("Canonical URL of the LOINC ValueSet?", validate=NotEmptyValidator),
    version = questionary.text("Version?", validate=NotEmptyValidator),
    title = questionary.text("Title (for humans)?", validate=NotEmptyValidator),
    name = questionary.text("Name (for machines), and id?", validate=NotEmptyValidator),
    status = questionary.select("Status", choices=["draft", "active", "retired", "unknown"])
).ask()
vs_answers.update({
    "id": cs_answers["name"],
    })
valueset = ValueSet(**vs_answers)

valueset_concepts = []
for concept in defined_concepts:
    loinc = concept["loinc"]
    if loinc is None:
        continue
    valid, display = fhir_api.lookup_code_display("http://loinc.org", loinc)
    if not valid:
        continue
    compose_concept = ValueSetComposeIncludeConcept(**{
        "code": loinc,
        "display": display
        })
    print(compose_concept.json())
    valueset_concepts.append(compose_concept)

valueset.compose = ValueSetCompose(**{
    "include": [{
        "system": "http://loinc.org",
        "concept": valueset_concepts
        }]})

print(valueset.json())
