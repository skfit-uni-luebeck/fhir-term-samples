package createresources;

import lombok.Builder;
import lombok.Data;
import org.hl7.fhir.r4.model.codesystems.PublicationStatus;
import org.hl7.fhir.r4.model.codesystems.ResourceStatus;

@SuppressWarnings({"HttpUrlsUsage", "unused"})
@Builder(toBuilder = true)
@Data
public class ResourceAttributes {
    private final String idName;
    private final String title;
    private final String version;
    private final String url;
    private final PublicationStatus publicationStatus = PublicationStatus.DRAFT;

    public static ResourceAttributes codeSystem() {
        return ResourceAttributes.builder()
                .idName("cs-lab-codes")
                .title("Lab Codes CS")
                .url("http://example.org/fhir/CodeSystem/cs-lab-codes")
                .version("20210705")
                .build();
    }

    public static ResourceAttributes loincValueset() {
        return ResourceAttributes.builder()
                .idName("vs-lab-codes-loinc")
                .title("Lab Codes LOINC VS")
                .url("http://example.org/fhir/ValueSet/vs-lab-codes-loinc")
                .version("20210705")
                .build();
    }

    public static ResourceAttributes conceptMap() {
        return ResourceAttributes.builder()
                .idName("cm-lab-codes-loinc")
                .title("Lab Codes to LOINC CM")
                .url("http://example.org/fhir/ConceptMap/cm-lab-codes")
                .version("20210705")
                .build();
    }
}
