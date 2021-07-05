package authentication;

import ca.uhn.fhir.rest.client.api.IGenericClient;
import fhirwrapper.FhirClientWrapper;
import org.hl7.fhir.r4.model.CapabilityStatement;

public class Authenticate {

    public static void main(String[] args) {
        IGenericClient fhirClient = FhirClientWrapper.getFhirClient();
        CapabilityStatement capabilities = fhirClient.capabilities().ofType(CapabilityStatement.class).execute();
        //query the metadata from the TS and parse the software component
        System.out.printf("%s %s%n", capabilities.getSoftware().getName(), capabilities.getSoftware().getVersion());
    }
}
