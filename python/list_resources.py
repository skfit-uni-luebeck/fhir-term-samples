from get_session import FhirApi
from fhir.resources.bundle import Bundle
from rich import print

fhir_api = FhirApi()
bundle : Bundle = fhir_api.request_and_parse_fhir("CodeSystem", Bundle)
resources = [r.resource for r in bundle.entry]
resources.sort(key=lambda r: (r.name if r.title is None else r.title, r.version))
for r in resources:
    name = r.name if r.title is None else r.title
    print(f" - '{name}' ({r.url}, version {r.version})")
