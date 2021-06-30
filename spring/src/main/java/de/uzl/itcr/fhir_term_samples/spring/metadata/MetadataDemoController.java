package de.uzl.itcr.fhir_term_samples.spring.metadata;

import ca.uhn.fhir.context.FhirContext;
import de.uzl.itcr.fhir_term_samples.spring.FhirService;
import lombok.SneakyThrows;
import org.hl7.fhir.r4.model.CapabilityStatement;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;

import java.net.MalformedURLException;
import java.net.URISyntaxException;
import java.util.Map;

/**
 * a simple controller that returns the name and version of the software on /metadata/version
 */
@Controller
@RequestMapping("/metadata")
public class MetadataDemoController {

  /**
   * inject the FHIR service into the controller
   */
  private final FhirService fhirService;
  private final FhirContext fhirContext;

  final CapabilityStatement metadata;

  public MetadataDemoController(FhirService fhirService, FhirContext fhirContext) throws MalformedURLException, URISyntaxException {
    this.fhirService = fhirService;
    this.fhirContext = fhirContext;
    this.metadata = fhirService.getResourceFromPath("metadata", CapabilityStatement.class);
  }

  /**
   * return the metadata serialized to indented JSON
   *
   * @param model the MVC model
   * @return the simple viewer template
   */
  @GetMapping
  public ModelAndView metadata(Map<String, Object> model) {
    model.put("data", fhirContext.newJsonParser()
        .setPrettyPrint(true)
        .encodeResourceToString(metadata));
    model.put("isJson", true);
    return new ModelAndView("simpleData", model);
  }

  /**
   * render a page that states the name and version of this application
   *
   * @param model the MVC model
   * @return the simple viewer template
   */
  @SneakyThrows
  @GetMapping("/version")
  public ModelAndView queryVersion(Map<String, Object> model) {
    model.put("data", String.format("%s %s", metadata.getSoftware().getName(), metadata.getSoftware().getVersion()));
    return new ModelAndView("simpleData", model);
  }
}
