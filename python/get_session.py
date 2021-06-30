from requests import Session

class FhirApi:
    "encapsulate a connection to a FHIR TS"
    session : Session # hold the requests session
    cert_file: str # path to the certificate
    endpoint: str # the endpoint of the FHIR TS

    def __init__(self, cert_file: str = "dfn.pem", endpoint: str = "https://terminology-highmed.medic.medfak.uni-koeln.de/fhir"):
        self.session = Session()
        self.cert_file = cert_file
        self.session.cert = self.cert_file
        self.endpoint = endpoint.rstrip("/") # remove slash at end to make sure that joining works
    
    def build_url(self, path: str) -> str:
        return self.endpoint + "/" + path.lstrip("/") # remove slash at beginning also
    
    def request_and_parse_fhir(self, path: str, resource):
        " request from the given path and try to convert to the given FHIR resource"
        request_url = self.build_url(path)
        response = self.session.get(request_url)
        if response.status_code >= 200 and response.status_code < 300:
            try: # very simplistic error handling
                return resource(**response.json()) # parse with given class
            except Exception as e:
                raise ValueError("Parsing the response was not possible")
        else:
            raise SystemError(f"Error requesting from {request_url}, status code {response.status_code}")
