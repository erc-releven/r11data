"""Module interface for query_templates"""

import importlib.resources
import sys

templates_path = importlib.resources.files("r11data.tabular.deaths.query_templates")
module = sys.modules[__name__].__dict__

for query_file in templates_path.rglob("*.rq"):
    query_name = f"{query_file.stem}_template"
    with open(query_file) as f:
        query_content: str = f.read()

    module.update({query_name: query_content})
