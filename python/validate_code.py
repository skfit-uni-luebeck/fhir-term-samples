from get_session import FhirApi
from fhir.resources.bundle import Bundle
from fhir.resources.parameters import Parameters
from rich import print, inspect
import questionary

# request the list of code systems from API
fhir_api = FhirApi()
bundle : Bundle = fhir_api.request_and_parse_fhir("CodeSystem", Bundle)
resources = [r.resource for r in bundle.entry]
resources.sort(key=lambda r: (r.name if r.title is None else r.title, r.version))
# sort by name and version to make the list pretty
options = [questionary.Choice(f"{r.name} ({r.url} v{r.version})", value=(r.url, r.version)) for r in resources]
# options contains choices for each CodeSystem that the Ontoserver knows.
# The value is a tuple of (url, version) to enable versioned query
answers = questionary.form(
    codesystem = questionary.select("Code System to use?", choices=options),
    code = questionary.text("Enter a code: ")
).ask()
# prompt user for CodeSystem and code interactively, results available in answers dict
url, version = answers["codesystem"]
code = answers["code"]
request_path = f"CodeSystem/$validate-code?code={code}&url={url}&version={version}"
parameters: Parameters = fhir_api.request_and_parse_fhir(request_path, Parameters)
# retrieve the parameters as applicable from the Parameters class
result = next(p for p in parameters.parameter if p.name == 'result').valueBoolean
if result:
    # True means that the concept is in the CodeSystem
    display = next(p for p in parameters.parameter if p.name == 'display').valueString
    print(f"The code '{code}' ('{display}') belongs to the CodeSystem.")
else:
    message = next(p for p in parameters.parameter if p.name == 'message').valueString
    print(message)

