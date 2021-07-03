from requests import Session
from rich import print
from fhir.resources.bundle import Bundle
from fhir.resources.parameters import Parameters, ParametersParameter
from typing import Optional, Tuple
from urllib.request import getproxies

class FhirApi:
    "encapsulate a connection to a FHIR TS"
    session : Session # hold the requests session
    cert_file: str # path to the certificate
    endpoint: str # the endpoint of the FHIR TS
    print_url: bool # if true, request URLs will be printed

    def __init__(self, cert_file: str = "dfn.pem", endpoint: str = "https://terminology-highmed.medic.medfak.uni-koeln.de/fhir", print_url: bool = True):
        self.session = Session()
        self.cert_file = cert_file
        # set proxy from environment (HTTP_PROXY/HTTPS_PROXY) if set
        if len(getproxies()) > 0:
            self.session.proxies = getproxies()
            print(f"Using proxies: {getproxies()}")
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

    def get_param_by_name(self, parameters, name) -> Optional[ParametersParameter]:
        return next((p for p in parameters.parameter if p.name == name), None)

    def lookup_code_display(self, url: str, code: str, version: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        request_url = f"CodeSystem/$validate-code?url={url}&code={code}"
        if version is not None:
            request_url += f"&version={version}"
        params: Parameters = self.request_and_parse_fhir(request_url, Parameters)
        valid_code = self.get_param_by_name(params, "result").valueBoolean
        if not valid_code:
            message = self.get_param_by_name(params, "message").valueString
            print(message)
            return (False, None)
        display = self.get_param_by_name(params, "display").valueString
        return (valid_code, display)

    def request_bundle(self, path: str) -> Bundle:
        return self.request_and_parse_fhir(path, Bundle)
