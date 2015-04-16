from base import wraps

_panel_template = """
<div class="panel {klass}">
  {heading}
  <div class="panel-body">
    {content}
  </div> <!-- end panel-body -->
</div> <!-- end panel -->
"""

_panel_heading_template = """
  <div class="panel-heading">
    <h3 class="panel-title">
      {title}
    </h3>
  </div> <!-- end panel-heading -->
"""


def panel(title=None, klass="panel-default"):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            heading = ''
            if title:
                heading = _panel_heading_template.format(title=title)
            content = func(*args, **kwargs)
            return _panel_template.format(content=content, heading=heading, klass=klass)
        return inner
    return decorator
