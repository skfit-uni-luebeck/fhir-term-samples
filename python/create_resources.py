import sqlite3
from get_session import FhirApi
import get_session
from fhir.resources.valueset import ValueSet, ValueSetCompose, ValueSetComposeInclude, ValueSetComposeIncludeConcept
from fhir.resources.codesystem import CodeSystem, CodeSystemConcept, CodeSystemConceptProperty, CodeSystemProperty
from fhir.resources.conceptmap import ConceptMap, ConceptMapGroup, ConceptMapGroupElement, ConceptMapGroupElementTarget
from fhir.resources.parameters import Parameters
from fhir.resources.bundle import Bundle
from rich import print, inspect
import questionary
import urllib.parse
from questionary import Validator, ValidationError
from typing import List, Dict
import json

equivalence_choices = ["relatedto", "equivalent", "equal", "wider", "subsumes", "narrower", "specializes", "inexact", "unmatched", "disjoint"]

class NotEmptyValidator(Validator):
    "validate that the value in non-empty"
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Please enter a value",
                cursor_position=len(document.text),
            )

class EquivalenceValidator(Validator):
    "validate that the value is one of the permitted equivalence codes"
    def validate(self, document):
        if document.text not in equivalence_choices:
            raise ValidationError(
                message=f"Please enter one of: {'|'.join(equivalence_choices)}",
                cursor_position=len(document.text)
            )

fhir_api = FhirApi(endpoint="http://localhost/fhir", cert_file=None, print_url=False)
#fhir_api = FhirApi(endpoint="https://r4.ontoserver.csiro.au/fhir", cert_file=None)
# select everything from the db
sql = "SELECT code, display, unit, loinc FROM lab_codes;"
sqlconn = sqlite3.connect("../legacydb.sqlite3")
sqlconn.row_factory = sqlite3.Row # access rows using Row interface, instead of tuples
cur = sqlconn.cursor()
# list the available concepts from the DB as list of dict
# loads everything into memory. Propably not a good idea for all real applications...
defined_concepts : List[Dict[str, str]] = []
for row in cur.execute(sql):
    defined_concepts.append(dict(zip(row.keys(), row)))
    # this produces a list of dicts with the column names as keys

# query for attributes of the FHIR CodeSystem
cs_answers = questionary.form(
    url = questionary.text("Canonical URL of the CodeSystem?", validate=NotEmptyValidator),
    valueSet = questionary.text("Canonical URL of the implicit ValueSet?", validate=NotEmptyValidator),
    version = questionary.text("Version?", validate=NotEmptyValidator),
    title = questionary.text("Title (for humans)?", validate=NotEmptyValidator),
    name = questionary.text("Name (for machines), and id?", validate=NotEmptyValidator),
    status = questionary.select("Status", choices=["draft", "active", "retired", "unknown"]),
    description = questionary.text("Description?")
).ask()
if not cs_answers["description"].strip():
    # don't serialize null descriptions
    cs_answers["description"] = None
cs_answers.update({
    "id": cs_answers["name"],
    # the name is used as the ID for simplicity
    "content": "complete",
    # content will always be complete (no other concepts are defined elsewhere)
    })
# the keys of the answers correspond 1:1 to the FHIR attributes, so creating the CS is easy
code_system = CodeSystem(**cs_answers)

# the data defines units for the concepts. Store these as a Property for each concept
code_system.property = [CodeSystemProperty(**{"code": "unit", "type": "string"})]
# generate concepts from the database
code_system.concept = [CodeSystemConcept(**{
    "code": c["code"],
    "display": c["display"],
    "property": [CodeSystemConceptProperty(**{
        "code": "unit",
        "valueString": c["unit"]
        })]
    }) for c in defined_concepts]
print("\nGenerated CodeSystem:")
print(code_system.json())
# write the generated CodeSystem to a file, indented
with open("codesystem.fhir.json", "w") as jf:
    # code_system.json() does not produce a dict, but a String. Parse that as JSON and then dump it
    json.dump(json.loads(code_system.json()), jf, indent=2)
    print("Wrote CodeSystem to codesystem.fhir.json\n")

# This database defines a LOINC valueset of concepts that are mappable from the internal codes.
# We should define this valueset as another resource to use that in the ConceptMap we are going to define below,
# since ConceptMaps are defined over ValueSets, which define the context of the mapping.
# Query for attributes of the FHIR ValueSet for LOINC
vs_answers = questionary.form(
    url = questionary.text("Canonical URL of the LOINC ValueSet?", validate=NotEmptyValidator),
    version = questionary.text("Version?", validate=NotEmptyValidator),
    title = questionary.text("Title (for humans)?", validate=NotEmptyValidator),
    name = questionary.text("Name (for machines), and id?", validate=NotEmptyValidator),
    status = questionary.select("Status", choices=["draft", "active", "retired", "unknown"]),
    description = questionary.text("Description?")
).ask()
if not vs_answers["description"].strip():
    vs_answers["description"] = None
vs_answers.update({
    "id": vs_answers["name"],
    })
valueset = ValueSet(**vs_answers)

# enumerate the LOINC concepts defined by the mapping DB
valueset_concepts = []
loinc_concepts = []
for concept in defined_concepts:
    loinc = concept["loinc"]
    if loinc is None:
        # loinc is nullable in DB
        continue
    # verify that the concept is a valid LOINC code, and lookup its Display, as that is not defined
    # in the DB. lookup_code_display queries $validate-code for that, since that operation returns
    # the display along with the validation.
    valid, display = fhir_api.lookup_code_display("http://loinc.org", loinc)
    if not valid:
        # skip the concepts that are invalid
        continue
    loinc_concepts.append({
        "code": loinc,
        "display": display
        })

valueset.compose = ValueSetCompose(**{
    "include": [{
        "system": "http://loinc.org",
        "concept": [ValueSetComposeIncludeConcept(**c) for c in loinc_concepts]
    }]})

print("\nGenerated ValueSet:")
print(valueset.json())
with open("loinc-valueset.fhir.json", "w") as jf:
    json.dump(json.loads(valueset.json()), jf, indent=2)
    print("Wrote ValueSet to loinc-valueset.fhir.json\n")

# lastly, define the ConceptMap for mapping from local codes to LOINC
cm_answers = questionary.form(
    url = questionary.text("Canonical URL of the ConceptMap?", validate=NotEmptyValidator),
    version = questionary.text("Version?", validate=NotEmptyValidator),
    title = questionary.text("Title (for humans)?", validate=NotEmptyValidator),
    name = questionary.text("Name (for machines), and id?", validate=NotEmptyValidator),
    status = questionary.select("Status", choices=["draft", "active", "retired", "unknown"]),
    description = questionary.text("Description?")
).ask()
if not cm_answers["description"].strip():
    cm_answers["description"] = None
cm_answers.update({
    "id": cm_answers["name"],
    "sourceUri": cs_answers["valueSet"],
    "targetUri": vs_answers["url"],
    # source and target are for ValueSets (implicit VS with all concepts for source codes, and
    # the URL of the LOINC target VS, since mappings are context-dependent
    })

map_elements: List[ConceptMapGroupElement] = []
for concept in defined_concepts:
    code = concept["code"]
    display = concept["display"]
    cd = f"{code}| {display}|"
    if "loinc" not in concept or concept["loinc"] is None:
        print(f"{cd} has no LOINC mapping")
        continue
    loinc = next((l for l in loinc_concepts if l["code"] == concept["loinc"]), None)
    if loinc is None:
        print(f"{cd} has no valid LOINC concept")
        continue
    loinc_cd = f"{loinc['code']}| {loinc['display']}|"
    # equivalence has to be provided by the user. Autocomplete might speed up selection for a large
    # number of mapped concepts, and the Validator enforces a valid selection
    equivalence = questionary.autocomplete(f"Equivalence for {cd} -> {loinc_cd}?",
            choices=equivalence_choices, validate=EquivalenceValidator).ask()
    # mappings can have a comment that explains the equivalence, etc.
    comment = questionary.text(f"Comment for {cd} -> {loinc_cd}?").ask()
    if not comment.strip():
        comment = None
    map_elements.append(ConceptMapGroupElement(**{
        "code": code,
        "display": display,
        "target": [{
            "code": loinc["code"],
            "display": loinc["display"],
            "equivalence": equivalence,
            "comment": comment
            }]}))
group = ConceptMapGroup(**{
    "source": cs_answers["url"],
    "target": vs_answers["url"],
    "element": map_elements
})
cm_answers.update({
    "group": [group]})
conceptmap = ConceptMap(**cm_answers)

print("\nGenerated ConceptMap:")
print(conceptmap.json())
with open("conceptmap.fhir.json", "w") as jf:
    json.dump(json.loads(conceptmap.json()), jf, indent=2)
    print("Wrote ConceptMap to conceptmap.fhir.json")
