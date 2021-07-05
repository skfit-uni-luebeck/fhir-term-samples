package fhirwrapper;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.rest.client.api.IGenericClient;
import ca.uhn.fhir.rest.client.api.IRestfulClientFactory;
import lombok.SneakyThrows;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContexts;

import javax.net.ssl.SSLContext;
import java.io.IOException;
import java.net.URL;
import java.security.KeyManagementException;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.UnrecoverableKeyException;
import java.security.cert.CertificateException;

public class FhirClientWrapper {
    private static FhirContext fhirContext = null;

    private static final String keystoreFilename = "keystore.jks";
    private static final String keystorePassword = "pw";
    private static final String serverBase = "https://terminology-highmed.medic.medfak.uni-koeln.de/fhir";

    public static FhirContext getFhirContext() {
        if (fhirContext == null) {
            fhirContext = FhirContext.forR4();
            configureFhirContextClient();
        }
        return fhirContext;
    }

    @SneakyThrows
    private static void configureFhirContextClient() {
        URL keystorePath = ClassLoader.getSystemResource(keystoreFilename); //get keystore from src/main/resources
        char[] password = keystorePassword.toCharArray(); //password of keystore and key within keystore (can be different)
        SSLContext sslContext = SSLContexts.custom() //we need to load the material from the keystore
                .loadKeyMaterial(keystorePath, password, password)
                .build(); //trust material is added automatically from the system default
        CloseableHttpClient client = HttpClients.custom() //configure a HTTP client with the custom SSL context
                .setSSLContext(sslContext)
                .build();
        final IRestfulClientFactory restfulClientFactory = fhirContext.getRestfulClientFactory();
        restfulClientFactory.setHttpClient(client); //configure the client factory to use our HTTP client
    }

    public static IGenericClient getFhirClient() {
        if (fhirContext == null) getFhirContext(); //instantiate singleton
        return fhirContext.newRestfulGenericClient(serverBase);
    }
}
