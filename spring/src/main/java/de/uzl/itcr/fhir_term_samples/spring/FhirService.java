package de.uzl.itcr.fhir_term_samples.spring;

import ca.uhn.fhir.context.FhirContext;
import lombok.SneakyThrows;
import org.hl7.fhir.r4.model.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import java.net.MalformedURLException;
import java.net.URI;

@Service
public class FhirService {

  private final FhirContext fhirContext;
  private final RestTemplate fhirRestTemplate;
  private final URI endpoint = URI.create("https://terminology-highmed.medic.medfak.uni-koeln.de/fhir".replaceAll("/$", ""));

  @SneakyThrows
  public <T extends Resource> T getResourceFromPath(String path, Class<T> clazz, Object... variables) throws HttpClientErrorException {
    String resolved = String.format("%s/%s", endpoint, path);
    ResponseEntity<String> response = fhirRestTemplate.getForEntity(resolved, String.class, variables);
    if (response.getStatusCode().is2xxSuccessful())
      return fhirContext.newJsonParser().parseResource(clazz, response.getBody());
    throw new HttpClientErrorException(response.getStatusCode(), String.format("Error requesting %s", resolved.toString()));
  }

  public FhirService(FhirContext fhirContext, RestTemplate fhirRestTemplate) throws MalformedURLException {
    this.fhirContext = fhirContext;
    this.fhirRestTemplate = fhirRestTemplate;
  }
}
