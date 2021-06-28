import requests
from fhir.resources.capabilitystatement import CapabilityStatement
from rich import print

def url(endpoint, path):
    """append the provided path to the endpoint to build an url"""
    return f"{endpoint.rstrip('/')}/{path}"

endpoint = "https://terminology-highmed.medic.medfak.uni-koeln.de/fhir/"
sess = requests.Session() # create a persistent session/connection
cert_file = "../joshua_dfn.pem" # contains both certifacate and private key
#cert_file = ("../joshua_dfn.crt", "../joshua_dfn.key") # two files for public/private key
sess.cert = cert_file # applies to all requests initiated from this session
response = sess.get(url(endpoint, "metadata")) # issue the actual request (without preparing it)
conformance = CapabilityStatement(**response.json()) # parse as FHIR
software = conformance.software # access structure of FHIR resource
print(f"{software.name} version {software.version}")
