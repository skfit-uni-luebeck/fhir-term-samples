from get_session import FhirApi
from fhir.resources.bundle import Bundle
from fhir.resources.parameters import Parameters
from fhir.resources.valueset import ValueSet
from fhir.resources.codesystem import CodeSystem
from typing import List
from rich import print, inspect
import questionary

# request the list of code systems and valuesets from API
fhir_api = FhirApi(print_url=False)
vs_bundle : Bundle = fhir_api.request_and_parse_fhir("ValueSet", Bundle)
cs_bundle : Bundle = fhir_api.request_and_parse_fhir("CodeSystem", Bundle)
# we only consider CodeSystems that have the valueSet parameter defined, since only these can be expanded
cs: List[CodeSystem] = [r.resource for r in cs_bundle.entry \
        if r.resource.valueSet is not None]
vs: List[ValueSet] = [r.resource for r in vs_bundle.entry]

# create a list of textual values, and (url, version) pairs, using the valueSet canonical for CS
resources = [(f"ValueSet {v.url} version {v.version}", (v.url, v.version)) for v in vs]
resources.extend((f"CodeSystem {c.url} version {c.version}", (c.valueSet, c.version)) for c in cs)
#sort by name (can't unpack tuple in lambda)
resources.sort(key=lambda r: r[0])

# select a CodeSystem/ValueSet from the list
options = [questionary.Choice(text, value=(text,res)) for text, res in resources]
# options contains labels and (url, version) for all of the CS with implicit VS, and explicit VS
text, res = questionary.select("Resource to use?", choices=options).ask()
print(f"Selected {text}")
# a filter can be provided to the expand operation to only select matching codes
concept_filter: str = questionary.text("Enter a filter, or leave blank").ask()
request_path = f"ValueSet/$expand?version={res[1]}&url={res[0]}"
if concept_filter.strip():
    # empty strings in Python are Falsy
    request_path += f"&filter={concept_filter}"
#request the expansion from the server
vs: ValueSet = fhir_api.request_and_parse_fhir(request_path, ValueSet)
# prompt user for the matching code interactively
if len([c.system for c in vs.expansion.contains]) > 1:
    # if more than 1 CS is present in the expansion, we need to qualify codes with the associated URL
    codes = [(f"'{c.display}'='{c.code}' ({c.system})", (c.code, c.system, c.version)) for c in vs.expansion.contains]
else:
    codes = [(f"'{c.display}'='{c.code}'", (c.code, c.system, c.version)) for c in vs.expansion.contains]
sel_code, sel_url, sel_version = questionary.select("Which code do you want to inspect?", 
        choices=[questionary.Choice(c, value=a) for c, a in codes]).ask()
# create a lookup request for the selected concept
lookup_path = f"CodeSystem/$lookup?code={sel_code}&system={sel_url}"
# $lookup returns Parameters
parameters: Parameters = fhir_api.request_and_parse_fhir(lookup_path, Parameters)
def print_parameter_value(param_name: str, parameters: Parameters, print_name = None):
    "parse the provided Parameters instance, and print it to the screen. param_name is the key as provided by the response, and print_name, if present, is printed as a prefix."
    param = next((p for p in parameters.parameter if p.name == param_name), None)
    if param is None:
        return
    if param.valueString is not None:
        value = param.valueString
    elif param.part is not None:
        value = [p.json() for p in param.part]
    else:
        value = param.json()
    print_name = print_name if print_name is not None else param_name
    print(f"{print_name}: {value}")

print_parameter_value("name", parameters, "CodeSystem Name")
print_parameter_value("version", parameters, "CodeSystem Version")
print_parameter_value("display", parameters, "Code Display")
print_parameter_value("designation", parameters, "Code Designation")

