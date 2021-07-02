from get_session import FhirApi
from fhir.resources.valueset import ValueSet
from fhir.resources.bundle import Bundle
from rich import print, inspect
import questionary
import re
import urllib.parse

# use australian server to demonstrate availability of multiple SNOMED CT versions
fhir_api = FhirApi(print_url=True, endpoint="https://r4.ontoserver.csiro.au/fhir")
# request the list of all SNOMED CT version on this server
request_path = "CodeSystem?url=http://snomed.info/sct"
refset_re = r"sct\/(\d*)\/" # regex for retrieving the refset ID
version_re = r"(\d*)$" #regex for retrieving the version
snomed_bundle = fhir_api.request_bundle(request_path)
available_snomed = [{
    "title": s.resource.title,
    "versionUrl": s.resource.version,
    "refset": re.search(refset_re, s.resource.version).group(1),
    "version": re.search(version_re, s.resource.version).group(1)
    } for s in snomed_bundle.entry]
editions = list(set((f"'{x['title']}' (refset {x['refset']})", x["refset"]) for x in available_snomed))
if len(editions) > 1:
    edition = questionary.select("Which edition of SNOMED CT to use?", choices=[questionary.Choice(text, value=res) for text, res in sorted(editions, key=lambda x: x[0])]).ask()
else:
    _, edition = list(editions)[0]

versions_for_edition = sorted([x["version"] for x in available_snomed if x["refset"] == edition], reverse=True)
version = questionary.select("Which version of the selected refset to use?", choices=versions_for_edition).ask()
print(f"Using version {version} for refset {edition}")

ecl = questionary.text("ECL Expression?").ask()
encoded_ecl = urllib.parse.quote(ecl)
print(f"Encoded ECL expression: {encoded_ecl}")

expansion_url = f"ValueSet/$expand?url=http://snomed.info/sct/{edition}/version/{version}?fhir_vs=ecl/{encoded_ecl}"
vs: ValueSet = fhir_api.request_and_parse_fhir(expansion_url, ValueSet)

print(f"There are {vs.expansion.total} concepts in the expression:")
if vs.expansion.total > 0:
    for concept in vs.expansion.contains:
        print(f" - {concept.code} |{concept.display}|")
