package listresources;

import ca.uhn.fhir.rest.client.api.IGenericClient;
import fhirwrapper.FhirClientWrapper;
import org.hl7.fhir.r4.model.Bundle;
import org.hl7.fhir.r4.model.CodeSystem;

import java.util.Comparator;
import java.util.stream.Collectors;

public class ListResources {

    public static void main(String[] args) {
        IGenericClient fhirClient = FhirClientWrapper.getFhirClient();
        // standard pattern using IGenericClient for listing resources:
        // provide the class to search, then return as Bundle
        Bundle csBundle = fhirClient.search()
                .forResource(CodeSystem.class)
                .returnBundle(Bundle.class)
                .execute();
        // map the Bundle to a list of CodeSystems, since we know that only CS are
        // going to be present in the Bundle. Sort by URL and version ascending.
        csBundle.getEntry().stream().map(b -> (CodeSystem) b.getResource())
                .sorted(Comparator.comparing(CodeSystem::getUrl)
                .thenComparing(CodeSystem::getVersion)
        ).forEach(
                // print each entry to STDOUT
                entry -> System.out.printf("- CodeSystem '%s' (%s) version %s%n",
                        entry.getName(),
                        entry.getUrl(),
                        entry.getVersion())
                // Java type system ensures easy and consistent access to FHIR attributes
        );

    }
}
