from hubs.widgets.base import wraps

import jinja2

_panel_template = jinja2.Template("""
<div class="panel {{klass}}">
  {{heading}}
  <div class="pull-right widget-buttons">
    <!-- the AGPLv3 wrapper puts the source url in all responses -->
    <a href="{{source_url}}"><span class="glyphicon glyphicon-eye-open"></span></a>
    <a href="{{widget_url}}"><span class="glyphicon glyphicon-new-window"></span></a>
    <a href="#"><span class="glyphicon glyphicon-edit"></span></a>
  </div>
  <div class="panel-body">
    {{content}}
  </div> <!-- end panel-body -->
</div> <!-- end panel -->
""")

_panel_heading_template = jinja2.Template("""
  <div class="panel-heading">
    <h3 class="panel-title">
      {{title}}
    </h3>
  </div> <!-- end panel-heading -->
""")


def panel(title=None, klass="panel-default", key=None):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            heading = ''
            if title:
                heading = _panel_heading_template.render(title=title)
            content = func(*args, **kwargs)
            if key and not kwargs.get(key):
                return content
            return _panel_template.render(
                content=content,
                heading=heading,
                klass=klass(kwargs) if callable(klass) else klass,
                **kwargs)
        return inner
    return decorator
