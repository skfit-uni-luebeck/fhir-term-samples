from get_session import FhirApi
from fhir.resources.bundle import Bundle
from fhir.resources.parameters import Parameters
from fhir.resources.valueset import ValueSet
from fhir.resources.codesystem import CodeSystem
from typing import List
from rich import print, inspect
import questionary

complex_cs = ["http://snomed.info/sct", "http://loinc.org"]

# request the list of code systems from API
fhir_api = FhirApi(print_url=False)
vs_bundle : Bundle = fhir_api.request_and_parse_fhir("ValueSet", Bundle)
cs_bundle : Bundle = fhir_api.request_and_parse_fhir("CodeSystem", Bundle)
cs: List[CodeSystem] = [r.resource for r in cs_bundle.entry \
        if r.resource.valueSet is not None \
        and r.resource.url not in complex_cs]
vs: List[ValueSet] = [r.resource for r in vs_bundle.entry]

resources = [(f"ValueSet {v.url} version {v.version}", (v.url, v.version)) for v in vs]
resources.extend((f"CodeSystem {c.url} version {c.version}", (c.valueSet, c.version)) for c in cs)
resources.sort(key=lambda r: r[0])

options = [questionary.Choice(text, value=res) for text, res in resources]
# options contains choices for each CodeSystem that the Ontoserver knows.
# The value is a tuple of (url, version) to enable versioned query
res = questionary.select("Resource to use?", choices=options).ask()
concept_filter: str = questionary.text("Enter a filter, or leave blank").ask()
request_path = f"ValueSet/$expand?version={res[1]}&url={res[0]}"
if concept_filter.strip():
    request_path += f"&filter={concept_filter}"
vs: ValueSet = fhir_api.request_and_parse_fhir(request_path, ValueSet)
# prompt user for CodeSystem and code interactively, results available in answers dict
if len([c.system for c in vs.expansion.contains]) > 1:
    codes = [(f"'{c.display}'='{c.code}' ({c.system})", c.code) for c in vs.expansion.contains]
else:
    codes = [(f"'{c.display}'='{c.code}'", c.code) for c in vs.expansion.contains]
cs_url, cs_version = questionary.select("Code System of the code?", 
        choices=[questionary.Choice()).ask()
code = questionary.text("Code:").ask()
# if cs_version is not None:
#    request_path += f"&system-version={cs_version}"
# commented out because of bug in Ontoserver 6.2.x that prevents using system-version
parameters: Parameters = fhir_api.request_and_parse_fhir(request_path, Parameters)
# retrieve the parameters as applicable from the Parameters class
result = next(p for p in parameters.parameter if p.name == 'result').valueBoolean
if result:
    # True means that the concept is in the CodeSystem
    display = next(p for p in parameters.parameter if p.name == 'display').valueString
    print(f"The code '{code}' ('{display}') belongs to the ValueSet.")
else:
    message = next(p for p in parameters.parameter if p.name == 'message').valueString
    print(message)

