package authentication;

import ca.uhn.fhir.rest.client.api.IGenericClient;
import org.hl7.fhir.r4.model.CapabilityStatement;

import java.io.IOException;
import java.security.KeyManagementException;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.UnrecoverableKeyException;
import java.security.cert.CertificateException;
import fhirwrapper.FhirClientWrapper;

public class Authenticate {

    public static void main(String[] args) {
        try {
            IGenericClient fhirClient = FhirClientWrapper.getFhirClient(null, null, null);
            CapabilityStatement capabilities = fhirClient.capabilities().ofType(CapabilityStatement.class).execute();
            //query the metadata from the TS and parse the software component
            System.out.printf("%s %s%n", capabilities.getSoftware().getName(), capabilities.getSoftware().getVersion());
        } catch (UnrecoverableKeyException | CertificateException | NoSuchAlgorithmException | KeyStoreException | IOException | KeyManagementException e) {
            e.printStackTrace();
        }
    }
}
