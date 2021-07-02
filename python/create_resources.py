import sqlite3
from fhir.resources.valueset import ValueSet
from fhir.resources.codesystem import CodeSystem
from fhir.resources.conceptmap import ConceptMap
from fhir.resources.bundle import Bundle
from rich import print, inspect
import questionary
import urllib.parse
from questionary import Validator, ValidationError

class NotEmptyValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Please enter a value",
                cursor_position=len(document.text),
            )


sql = "SELECT code, display, unit, loinc FROM lab_codes;"
sqlconn = sqlite3.connect("../legacydb.sqlite3")
sqlconn.row_factory = sqlite3.Row # access rows using Row interface, instead of tuples
cur = sqlconn.cursor()

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
print(code_system.json())

for row in cur.execute(sql):
    print(row)
    inspect(row)
