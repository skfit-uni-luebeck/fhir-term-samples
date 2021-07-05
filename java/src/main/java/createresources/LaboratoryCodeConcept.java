package createresources;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;


public @Data
@AllArgsConstructor
class LaboratoryCodeConcept {
    private String code;
    private String display;
    private String unit;
    private String loinc;
}
