from get_session import FhirApi
from fhir.resources.bundle import Bundle
from fhir.resources.parameters import Parameters
from fhir.resources.valueset import ValueSet
from rich import print, inspect
import questionary

# request the list of code systems from API
fhir_api = FhirApi(print_url=False)
vs_bundle : Bundle = fhir_api.request_and_parse_fhir("ValueSet", Bundle)
resources = [(r.resource, r.fullUrl) for r in vs_bundle.entry]
resources.sort(key=lambda r: (r[0].name if r[0].title is None else r[0].title, r[0].version))
# sort by name and version to make the list pretty
options = [questionary.Choice(f"{r.name} ({r.url} v{r.version})", value=url) for r, url in resources]
# options contains choices for each CodeSystem that the Ontoserver knows.
# The value is a tuple of (url, version) to enable versioned query
vs_url : ValueSet = questionary.select("ValueSet to use?", choices=options).ask()
vs: ValueSet = fhir_api.request_from_url_parse_fhir(vs_url, ValueSet)
url = vs.url
version = vs.version
contained_systems = set([(i.system, i.version) for i in vs.compose.include])
# prompt user for CodeSystem and code interactively, results available in answers dict
options = [questionary.Choice(f"{cs[0]} version {cs[1]}", value=cs) for cs in contained_systems]
cs_url, cs_version = questionary.select("Code System of the code?", choices=options).ask()
code = questionary.text("Code:").ask()
request_path = f"ValueSet/$validate-code?code={code}&url={url}&version={version}&system={cs_url}"
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

