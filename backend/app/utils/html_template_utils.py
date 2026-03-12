import os

from jinja2 import Environment, FileSystemLoader

__base_dir = os.path.dirname(os.path.abspath(__file__))
__templates_dir = os.path.join(__base_dir, "..", "templates")
__env = Environment(loader=FileSystemLoader(__templates_dir))

import logging

logging.info(__templates_dir)


def render_template(template_name: str, context: dict) -> str:
    if not template_name.endswith(".html"):
        template_name = template_name + ".html"
    template = __env.get_template(template_name)
    return template.render(context)
