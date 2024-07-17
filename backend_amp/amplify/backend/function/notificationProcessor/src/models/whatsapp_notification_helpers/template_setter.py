from .constants import WhatsappNotificationTemplates


class WhatsappNotificationTemplateSetter:
    def __init__(self) -> None:
        self._template = {}

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, data):
        parameters, template_type = data

        template = getattr(WhatsappNotificationTemplates(), template_type)
        temp_template = template["template"]
        components = temp_template.get("components", []) or []
        for component in components:
            component_parameters = component.get("parameters", []) or []
            for parameter in component_parameters:
                parameter_type = parameter.get("type")
                if parameter_type:
                    if parameter_type != "text":
                        parameter[parameter_type]["link"] = (
                            parameter[parameter_type]["link"]
                        ).format(**parameters)
                    else:
                        parameter[parameter_type] = (
                            parameter[parameter_type]
                        ).format(**parameters)
        temp_template["components"] = components
        self._template = temp_template