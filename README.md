# UML to Pydantic Converter

This script is a Python utility that converts UML text notation in Plantuml into Pydantic classes. It automates the process of generating Pydantic classes based on UML class definitions, including handling inheritance and composition relationships.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Input](#input)
- [Output](#output)
- [Example](#example)
- [Contributing](#contributing)
- [License](#license)

## Requirements

Before using this script, ensure you have the following requirements:

- Python 3.x
- The `pydantic` library (`pip install pydantic`)

## Installation

You can download or clone this repository to your local machine. There is no need for additional installation steps.

## Usage

To use this script, follow these steps:

1. Import the required modules at the beginning of your Python script:

   ```python
   import re
   ```

2. Define your UML models as a string.

3. Call the `generate_pydantic_classes_from_uml` function with your UML models string as an argument. This function will return the Pydantic code as a string.

4. You can then save the generated Pydantic code to a Python file or use it in your project as needed.

## Input

The input to this script should be a string containing UML class and enumeration diagrams. The script uses regular expressions to extract class definitions, relationships, and enumerations from this input.

## Output

The script generates Pydantic class definitions based on the input UML diagrams. The output is a Python code string that defines Pydantic classes and enumerations. You can use this code in your Python projects to work with data that conforms to the UML specifications.

## Example

Here's an example of how to use the script:

```python
uml_models_str = """
class Car {
  numberOfDoors: int
  brand: string
}

class ElectricCar {
}

class ElectricMotor {
  +outputKW: float
}

 
Car <|-- ElectricCar

ElectricCar *-- "*" ElectricMotor
"""

pydantic_code = generate_pydantic_classes_from_uml(uml_models_str)

# Use pydantic_code in your project as needed.
```

In this example, the `uml_models_str` variable contains UML class and enumeration diagrams. Calling `generate_pydantic_classes_from_uml` with this input generates Pydantic code.



## Contributing

Contributions are welcome! If you'd like to improve this script or fix any issues, please fork the repository and submit a pull request. You can also open an issue to report bugs or suggest enhancements.

## License

This script is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it as needed.
