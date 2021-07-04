package fhirwrapper;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.rest.client.api.IGenericClient;
import ca.uhn.fhir.rest.client.api.IRestfulClientFactory;
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
    final static FhirContext fhirContext = FhirContext.forR4();

    public static IGenericClient withDefaultSettings() {
        try {
            //return getFhirClient("http://localhost/fhir", null, null);
            return getFhirClient("http://localhost/koeln/fhir", null, null);
            //return getFhirClient(null, null, null);
        } catch (UnrecoverableKeyException | CertificateException | NoSuchAlgorithmException | KeyStoreException | IOException | KeyManagementException e) {
            e.printStackTrace();
            System.exit(1);
        }
        return null;
    }

    public static IGenericClient getFhirClient(String serverBase, String keystoreFilename, String keystorePassword) throws UnrecoverableKeyException, CertificateException, NoSuchAlgorithmException, KeyStoreException, IOException, KeyManagementException {
        if (keystoreFilename == null) keystoreFilename = "keystore.jks";
        if (keystorePassword == null) keystorePassword = "pw";
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
        if (serverBase == null) serverBase = "https://terminology-highmed.medic.medfak.uni-koeln.de/fhir";
        return fhirContext.newRestfulGenericClient(serverBase);
    }
}
