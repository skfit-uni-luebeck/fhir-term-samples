from get_session import (
    FhirApi,
    NotEmptyValidator,
    ValueListValidator,
    ParametersValueTypeValidator,
)
from rich import print
from fhir.resources.bundle import Bundle
from fhir.resources.parameters import Parameters, ParametersParameter
from fhir.resources.codesystem import CodeSystem
from typing import List
import questionary


fhir_api = FhirApi()
cs_bundle: Bundle = fhir_api.request_and_parse_fhir("CodeSystem", Bundle)
cs_list: List[CodeSystem] = [r.resource for r in cs_bundle.entry]
cs_options = [
    questionary.Choice(f"{r.url} {r.version}", value=(r.url, r.version))
    for r in cs_list
]
cs_options.sort(key=lambda c: c.value)

sel_cs, sel_cs_version = questionary.select("CodeSystem", choices=cs_options).ask()
print(sel_cs, sel_cs_version)


add_more_prop = True
parameter_properties = []
while add_more_prop:
    code = questionary.text("Code for property?", validate=NotEmptyValidator).ask()
    valueChoices = [
        "valueCode",
        "valueCoding",
        "valueString",
        "valueInteger",
        "valueBoolean",
        "valueDateTime",
    ]
    valueType = questionary.autocomplete(
        "Value type?", choices=valueChoices, validate=ValueListValidator(valueChoices)
    ).ask()
    if valueType == "valueBoolean":
        value = questionary.confirm("Is the value True?").ask()
    else:
        value = questionary.text(
            "Value of the property?", validate=ParametersValueTypeValidator(valueType)
        ).ask()
    parameter_properties.append(
        ParametersParameter(
            **{
                "name": "property",
                "part": [
                    ParametersParameter(**{"name": "code", "valueCode": code}),
                    ParametersParameter(**{"name": "value", valueType: value}),
                ],
            }
        )
    )
    request_parameters = Parameters(
        **{
            "parameter": [
                {"name": "system", "valueUri": sel_cs},
                {"name": "version", "valueString": sel_cs_version},
            ]
            + parameter_properties
        }
    )
    print(request_parameters.json())
    add_more_prop = questionary.confirm("Continue adding properties?").ask()

out_params = fhir_api.post_parameters_operation("CodeSystem/$find-matches", request_parameters)
if out_params is None:
    exit(1)
print(out_params.json(indent=2))
