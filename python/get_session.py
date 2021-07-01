from requests import Session
from rich import print

class FhirApi:
    "encapsulate a connection to a FHIR TS"
    session : Session # hold the requests session
    cert_file: str # path to the certificate
    endpoint: str # the endpoint of the FHIR TS
    print_url: bool # if true, request URLs will be printed

    def __init__(self, cert_file: str = "dfn.pem", endpoint: str = "https://terminology-highmed.medic.medfak.uni-koeln.de/fhir", print_url: bool = True):
        self.session = Session()
        self.cert_file = cert_file
        self.session.cert = self.cert_file
        self.endpoint = endpoint.rstrip("/") # remove slash at end to make sure that joining works
        self.print_url = print_url
    
    def build_url(self, path: str) -> str:
        return self.endpoint + "/" + path.lstrip("/") # remove slash at beginning also
    
    def request_from_url_parse_fhir(self, url: str, resource):
        if self.print_url:
            print(f"Requesting from {url}")
        response = self.session.get(url)
        if response.status_code >= 200 and response.status_code < 300:
            try: # very simplistic error handling
                j = response.json()
                if j["resourceType"] == "ValueSet" and "status" not in j:
                   j["status"] = "unknown" 
                return resource(**j) # parse with given class
            except Exception as e:
                raise ValueError(f"Parsing the response was not possible") from e
        else:
            raise SystemError(f"Error requesting from {url}, status code {response.status_code}")

    def request_and_parse_fhir(self, path: str, resource):
        " request from the given path and try to convert to the given FHIR resource"
        request_url = self.build_url(path)
        return self.request_from_url_parse_fhir(request_url, resource)
