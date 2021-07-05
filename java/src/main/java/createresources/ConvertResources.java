package createresources;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.rest.client.api.IGenericClient;
import fhirwrapper.FhirClientWrapper;
import org.hl7.fhir.instance.model.api.IBaseParameters;
import org.hl7.fhir.r4.model.*;

import java.sql.Connection;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Scanner;

@SuppressWarnings("HttpUrlsUsage")
public class ConvertResources {
    public static void main(String[] args) {
        LinkedList<LaboratoryCodeConcept> concepts = SqliteConnection.selectAll();
        IGenericClient fhirClient = FhirClientWrapper.getFhirClient();
        concepts.forEach(c -> System.out.println(c.toString()));

        ResourceAttributes codeSystemAttributes = ResourceAttributes.codeSystem();
        CodeSystem codeSystem = new CodeSystem()
                .setUrl(codeSystemAttributes.getUrl())
                .setName(codeSystemAttributes.getIdName())
                .setTitle(codeSystemAttributes.getTitle())
                .setVersion(codeSystemAttributes.getVersion());
        codeSystem.setId(codeSystemAttributes.getIdName()); // returns Resource instead of CodeSystem

        codeSystem.addProperty().setCode("unit").setType(CodeSystem.PropertyType.STRING);
        // allows for storing the Unit column
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

        // lookup all LOINC codes display, and validate them
        HashMap<String, String> loincConcepts = new HashMap<>();
        concepts.forEach(dbConcept -> {
            if (dbConcept.getLoinc() == null) return;

            Parameters validateParameters = new Parameters();
            // validateParameters contains the Code-Value pair to lookup
            validateParameters.addParameter()
                    .setName("url")
                    .setValue(new UriType("http://loinc.org"));
            validateParameters.addParameter()
                    .setName("code")
                    .setValue(new StringType(dbConcept.getLoinc()));
            // execute the operation validate-code with the provided parameters
            Parameters outParams = fhirClient.operation()
                    .onType(CodeSystem.class)
                    .named("$validate-code")
                    .withParameters(validateParameters)
                    .useHttpGet()
                    .execute();
            // ValueSet/$expand and other operations are callable in the same fashion using HAPI FHIR

            boolean isValidLoinc = outParams.getParameterBool("result");
            if (isValidLoinc) {
                // display contains the "name" of the LOINC term
                String display = outParams.getParameter("display").toString();
                String codeDisplay = String.format("%s| %s|",
                        dbConcept.getLoinc(), display);
                System.out.printf("Valid LOINC: %s%n", codeDisplay);
                loincConcepts.put(dbConcept.getLoinc(), display);
            } else {
                // if the concept is not valid, the server returns a message parameter
                System.out.printf("INVALID LOINC: %s%n",
                        outParams.getParameter("message").toString());
            }
        });

        // create the ValueSet in the same fashion as the CodeSystem
        ResourceAttributes valueSetAttributes = ResourceAttributes.loincValueset();
        ValueSet loincValueSet = new ValueSet()
                .setUrl(valueSetAttributes.getUrl())
                .setName(valueSetAttributes.getIdName())
                .setTitle(valueSetAttributes.getTitle())
                .setVersion(valueSetAttributes.getVersion());
        loincValueSet.setId(valueSetAttributes.getIdName());

        ValueSet.ConceptSetComponent valueSetInclude = loincValueSet.getCompose()
                .addInclude()
                .setSystem("http://loinc.org"); // we know it's LOINC
        loincConcepts.forEach((loinc, display) -> valueSetInclude.addConcept()
                .setCode(loinc)
                .setDisplay(display));

        System.out.printf("Encoded ValueSet:%n%s%n", FhirClientWrapper.getFhirContext()
                .newJsonParser().setPrettyPrint(true)
                .encodeResourceToString(loincValueSet));

        // creating the ConceptMap pretty much identical to the above patterns and not shown here...
    }
}
