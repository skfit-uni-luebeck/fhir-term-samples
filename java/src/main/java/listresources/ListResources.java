package listresources;

import ca.uhn.fhir.rest.client.api.IGenericClient;
import fhirwrapper.FhirClientWrapper;
import org.hl7.fhir.r4.model.Bundle;
import org.hl7.fhir.r4.model.CodeSystem;

import java.util.Comparator;
import java.util.stream.Collectors;

public class ListResources {

    public static void main(String[] args) {
        IGenericClient fhirClient = FhirClientWrapper.withDefaultSettings();
        Bundle csBundle = fhirClient.search()
                .forResource(CodeSystem.class)
                .returnBundle(Bundle.class)
                .execute();
        csBundle.getEntry().stream().map(b -> (CodeSystem) b.getResource())
                .sorted(Comparator.comparing(CodeSystem::getUrl)
                .thenComparing(CodeSystem::getVersion)
        ).forEach(
                entry -> System.out.printf("CodeSystem '%s' (%s) version %s%n",
                        entry.getName(),
                        entry.getUrl(),
                        entry.getVersion())
        );

    }
}
