package createresources;

import org.hl7.fhir.r4.model.CodeSystem;

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


    }
}
