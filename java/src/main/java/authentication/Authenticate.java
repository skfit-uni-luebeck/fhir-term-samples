package authentication;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.rest.client.api.IGenericClient;
import ca.uhn.fhir.rest.client.api.IRestfulClientFactory;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContexts;
import org.hl7.fhir.r4.model.CapabilityStatement;

import javax.net.ssl.SSLContext;
import java.io.IOException;
import java.net.URL;
import java.security.KeyManagementException;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.UnrecoverableKeyException;
import java.security.cert.CertificateException;

public class Authenticate {

    public static void main(String[] args) {
        URL keystorePath = ClassLoader.getSystemResource("keystore.jks"); //get keystore from src/main/resources
        char[] password = "pw".toCharArray(); //password of keystore and key within keystore (can be different)
        try {
            SSLContext sslContext = SSLContexts.custom() //we need to load the material from the keystore
                    .loadKeyMaterial(keystorePath, password, password)
                    .build(); //trust material is added automatically
            CloseableHttpClient client = HttpClients.custom() //configure a HTTP client with the custom SSL context
                    .setSSLContext(sslContext)
                    .build();
            final FhirContext fhirContext = FhirContext.forR4(); //do this exactly once for the lifetime of the app!
            final IRestfulClientFactory restfulClientFactory = fhirContext.getRestfulClientFactory();
            restfulClientFactory.setHttpClient(client); //configure the client factory to use our HTTP client
            final String serverBase = "https://terminology-highmed.medic.medfak.uni-koeln.de/fhir";
            IGenericClient fhirClient = fhirContext.newRestfulGenericClient(serverBase); //this will use our HTTP client
            CapabilityStatement capabilities = fhirClient.capabilities().ofType(CapabilityStatement.class).execute();
            //query the metadata from the TS and parse the software component
            System.out.printf("%s %s%n", capabilities.getSoftware().getName(), capabilities.getSoftware().getVersion());
        } catch (NoSuchAlgorithmException | KeyStoreException | UnrecoverableKeyException | CertificateException | IOException | KeyManagementException e) {
            e.printStackTrace();
        }
    }
}
