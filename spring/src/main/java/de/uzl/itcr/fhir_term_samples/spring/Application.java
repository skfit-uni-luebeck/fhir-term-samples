package de.uzl.itcr.fhir_term_samples.spring;

import ca.uhn.fhir.context.FhirContext;
import lombok.Data;
import lombok.SneakyThrows;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContexts;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.core.io.Resource;
import org.springframework.http.client.ClientHttpRequestFactory;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

import javax.net.ssl.SSLContext;

@SpringBootApplication
@EnableConfigurationProperties(FhirSslProps.class)
public class Application {

  /**
   * configure a RestTemplate that authenticates using the provided resource
   * @param fhirSslProps the configuration holder
   * @param keystoreResource the keystore resource, injected from the classpath
   * @return the configured REST template
   */
  @Bean
  @SneakyThrows
  public RestTemplate fhirRestTemplate(FhirSslProps fhirSslProps,
                                       @Value("classpath:keystore.jks") Resource keystoreResource) {
    SSLContext sslContext = SSLContexts.custom()
        .loadKeyMaterial(keystoreResource.getURL(),
            fhirSslProps.getKeystorePassword(),
            fhirSslProps.getKeyPassword())
        .build();
    CloseableHttpClient httpClient = HttpClients.custom().
        setSSLContext(sslContext).build(); //create a client from the SSL config
    ClientHttpRequestFactory clientRequestFactory = new HttpComponentsClientHttpRequestFactory(httpClient);
    //wrap the client using a RequestFactory and a RestTemplate
    return new RestTemplate(clientRequestFactory);
  }

  /**
   * the HAPI fhir context, initialized once
   *
   * @return the HAPI FHIR context
   */
  @Bean
  public FhirContext fhirContext() {
    return FhirContext.forR4();
  }

  public static void main(String[] args) {
    SpringApplication.run(Application.class, args);
  }

}

/**
 * holder for the configuration properties for talking to the FHIR TS endpoint
 */
@Data
@ConfigurationProperties(prefix = "fhir.ssl")
class FhirSslProps {
  /**
   * passwords that protect the keystore/private key
   */
  private char[] keystorePassword, keyPassword;
}
