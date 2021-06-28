import requests
from fhir.resources.capabilitystatement import CapabilityStatement
from rich import print

def url(endpoint, path):
    return f"{endpoint.rstrip('/')}/{path}"

endpoint = "https://terminology-highmed.medic.medfak.uni-koeln.de/fhir/"
sess = requests.Session()
cert_file = "../joshua_dfn.pem"
#cert_file = ("../joshua_dfn.crt", "../joshua_dfn.key")
sess.cert = cert_file
response = sess.get(url(endpoint, "metadata"))
conformance = CapabilityStatement(**response.json())
software = conformance.software
print(f"{software.name} version {software.version}")
