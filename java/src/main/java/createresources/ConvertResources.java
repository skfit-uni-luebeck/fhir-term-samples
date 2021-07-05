package createresources;

import fhirwrapper.FhirClientWrapper;
import org.hl7.fhir.r4.model.CodeSystem;
import org.hl7.fhir.r4.model.StringType;

import java.sql.Connection;
import java.util.LinkedList;
import java.util.Scanner;

public class ConvertResources {
    public static void main(String[] args) {
        LinkedList<LaboratoryCodeConcept> concepts = SqliteConnection.selectAll();
        concepts.forEach(c -> System.out.println(c.toString()));
        ResourceAttributes codeSystemAttributes = ResourceAttributes.codeSystem();
        CodeSystem codeSystem = new CodeSystem();
        codeSystem.setUrl(codeSystemAttributes.getUrl());
        codeSystem.setName(codeSystemAttributes.getIdName());
        codeSystem.setId(codeSystemAttributes.getIdName());
        codeSystem.setTitle(codeSystemAttributes.getTitle());
        codeSystem.setVersion(codeSystemAttributes.getVersion());

        codeSystem.addProperty().setCode("unit").setType(CodeSystem.PropertyType.STRING);

        concepts.forEach(dbConcept -> {

            CodeSystem.ConceptPropertyComponent unitProperty = new CodeSystem.ConceptPropertyComponent()
                    .setCode("unit")
                    .setValue(new StringType(dbConcept.getUnit()));
            codeSystem.addConcept(new CodeSystem.ConceptDefinitionComponent()
                    .setCode(dbConcept.getCode())
                    .setDisplay(dbConcept.getDisplay())
                    .addProperty(unitProperty)
            );
        });

        System.out.printf("Encoded CodeSystem:%n%s%n", FhirClientWrapper.getFhirContext()
                .newJsonParser().setPrettyPrint(true).encodeResourceToString(codeSystem));


    }
}
