import re


def get_number(text, value_if_not_number=None):
    pattern = r"[-+]?\d*\.\d+|\d+"

    if not isinstance(text, str):
        return value_if_not_number

    matches = re.findall(pattern, text)

    for match in matches:
        if "." in match:
            number = float(match)
        else:
            number = int(match)
        return number
    return value_if_not_number


def get_type(attr):
    if attr.lower() == "string":
        return "str"
    return attr


def find_matches(pattern, string):
    uml = {}
    matches = re.finditer(pattern, string)
    for match in matches:
        name = match.group(1).strip()
        content = match.group(2).strip()
        uml[name] = content
    return uml


def find_enums(uml_enums):
    literal_objects = {}
    for enum_name, enum_content in uml_enums.items():
        literal_str = f"{enum_name} = Literal[\n"

        attributes = enum_content.split("\n")

        for attribute in attributes:
            attribute = attribute.strip()
            if not attribute:
                continue

            s = e = ""

            if len(attribute) >= 2:
                s, *_, e = attribute

            if s == e == '"' or s == e == "'":
                literal_str += f"\t{attribute},\n"
            else:
                literal_str += f'\t"{attribute}",\n'

        literal_str += "]\n"
        literal_objects[enum_name] = literal_str
    return literal_objects


def get_inheritance_relationships(relationships):
    inheritance_relationships = {}
    for class_name, class_relationships in relationships.items():
        for relationship in class_relationships:
            if "<|--" == relationship["type"]:
                if relationship["related_class"] in inheritance_relationships:
                    inheritance_relationships[relationship["related_class"]].append(
                        class_name
                    )
                else:
                    inheritance_relationships[relationship["related_class"]] = [
                        class_name
                    ]
    return inheritance_relationships


def handle_inheritance(class_name, inheritance_relationships):
    pydantic_class_str = ""
    if class_name in inheritance_relationships:
        separator = ", "
        pydantic_class_str = f"class {class_name}({separator.join(inheritance_relationships[class_name])}):\n"
    else:
        pydantic_class_str = f"class {class_name}(BaseModel):\n"
    return pydantic_class_str


def find_classes(uml_classes, inheritance_relationships):
    pydantic_classes = {}
    for class_name, class_content in uml_classes.items():
        pydantic_class_str = handle_inheritance(class_name, inheritance_relationships)
        attribute_pattern = re.compile(r"(\+|-)?\s*(\w+)(?:\[\])?\s*:\s*(\w+(?:\[\])?)")
        attributes = re.findall(attribute_pattern, class_content)

        if len(attributes) == 0:
            pydantic_class_str += "\tpass\n"

        for _, attribute_name, attribute_type in attributes:
            if attribute_type[-2:] == "[]":
                pydantic_class_str += (
                    f"\t{attribute_name}: list[{get_type(attribute_type[:-2])}]\n"
                )
            else:
                pydantic_class_str += (
                    f"\t{attribute_name}: {get_type(attribute_type)}\n"
                )

        pydantic_classes[class_name] = pydantic_class_str
    return pydantic_classes


def sort_classes(pydantic_classes):
    class_code_pairs = list(pydantic_classes.items())
    codes = []

    for class_name, class_code in class_code_pairs:
        for code_idx, code in enumerate(codes):
            if class_name in code:
                codes.insert(code_idx, class_code)
                break

        codes.append(class_code)

    return codes


def create_python_code(literal_objects, pydantic_classes, inheritance_relationships):
    code = "from pydantic import BaseModel\nfrom typing import Literal\n\n"
    enum_list = list(literal_objects.values())
    pydantic_classes_list = sort_classes(pydantic_classes)

    for pydantic_str in enum_list + pydantic_classes_list:
        code += pydantic_str + "\n"
    return code


def get_composition_relationships(relationships):
    composition_relationships = {}
    for class_name, class_relationships in relationships.items():
        for relationship in class_relationships:
            if relationship["type"] in ["o--", "--", "*--"]:
                if class_name in composition_relationships:
                    composition_relationships[class_name].append(relationship)
                else:
                    composition_relationships[class_name] = [relationship]
    return composition_relationships


def get_code_without_pass(code):
    if "pass" in code:
        return code.split("pass")[0].strip() + "\n"
    return code


def add_params_to_classes(pydantic_classes, composition_relationships):
    for class_name, relationships in composition_relationships.items():
        for relationship in relationships:
            # if "*" in relationship["param2"]:
            #     if relationship["related_class"][-1] == "s":
            #         pydantic_classes[class_name] += f'\t{relationship["related_class"]}es: list[{relationship["related_class"]}]\n'
            #     else:
            #         pydantic_classes[class_name] += f'\t{relationship["related_class"]}s: list[{relationship["related_class"]}]\n'
            # else:

            if (
                relationship["type"] == "--"
                and relationship["param1"] == relationship["param2"] == ""
            ):
                continue

            pydantic_classes[class_name] = get_code_without_pass(
                pydantic_classes[class_name]
            )

            number_of_instances = get_number(relationship["param2"], None)
            if number_of_instances is None:
                number_of_instances = 0
            if number_of_instances > 1:
                if relationship["related_class"][-1] == "s":
                    pydantic_classes[
                        class_name
                    ] += f'\t{relationship["related_class"]}es: list[{relationship["related_class"]}]\n'
                else:
                    pydantic_classes[
                        class_name
                    ] += f'\t{relationship["related_class"]}s: list[{relationship["related_class"]}]\n'
            else:
                pydantic_classes[
                    class_name
                ] += f'\t{relationship["related_class"]}: {relationship["related_class"]}\n'


def find_relationships(uml_string):
    pattern = r'(\w+)\s*(?:"(.+)")?\s+(\*\-\-|<\|\-\-|o\-\-|\-\-)\s+(?:"(.+)")?\s*(\w+)'
    matches = re.findall(pattern, uml_string)

    extracted_relationships = {}

    for match in matches:
        class1, param1, relation, param2, class2 = match
        relationship_obj = {
            "type": relation,
            "related_class": class2,
            "param1": param1,
            "param2": param2,
        }
        if class1 in extracted_relationships:
            extracted_relationships[class1].append(relationship_obj)
        else:
            extracted_relationships[class1] = [relationship_obj]

    return extracted_relationships


def generate_pydantic_classes_from_uml(uml_models_str):
    class_pattern = re.compile(r"class\s+(\w+)\s*\{(.*?)\}", re.DOTALL)
    enum_pattern = re.compile(r"enum\s+(\w+)\s*\{([^}]*)\}", re.MULTILINE | re.DOTALL)

    uml_classes = find_matches(class_pattern, uml_models_str)
    uml_enums = find_matches(enum_pattern, uml_models_str)

    relationships = find_relationships(uml_models_str)
    inheritance_relationships = get_inheritance_relationships(relationships)
    composition_relationships = get_composition_relationships(relationships)

    literal_objects = find_enums(uml_enums)
    pydantic_classes = find_classes(uml_classes, inheritance_relationships)

    add_params_to_classes(pydantic_classes, composition_relationships)

    code = create_python_code(
        literal_objects, pydantic_classes, inheritance_relationships
    )

    return code
