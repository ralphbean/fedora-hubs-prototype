import dummy
import stats
import rules
import sticky

from base import AGPLv3

registry = {
    'dummy': dummy,
    'stats': stats,
    'rules': rules,
    'sticky': sticky,
}


def validate_registry(registry):
    """ Ensure that the widgets in the registry have the bits they need.
    - Check that a template is available and has a render callable.
    - Look for a data function, etc..
    - Ensure it has the right number of arguments, do things to help debugging.
    """
    raise NotImplementedError()
    for name, module in registry.items():
        pass

def prepare_registry(registry):
    """ Do things ahead of time that we can to the registry.
    - Wrap a cache layer around the data functions.
    - Wrap any chrome around the render functions.
    """
    for name, module in registry.items():
        # Wrap chrome around the render function
        module.render = module.template.render
        if hasattr(module, 'chrome'):
            module.render = module.chrome(module.render)

        # Put source links in all API results
        module.data = AGPLv3(name)(module.data)

        # TODO -- wrap a cache layer around the data functions
        #         do this only if the module provides a cache invalidator
        #         and warn in the logs if there's not one present?

# TODO -- actually call this
#validate_registry(registry)
prepare_registry(registry)

def render(module, request, session, widget, *args, **kwargs):
    """ Main API entry point.

    Call this to render a widget into HTML
    """


    # The API returns exactly this data.  Shared cache
    data = module.data(request, session, widget, *args, **kwargs)

    # Use the API data to fill out a template, and potentially decorate it.
    return module.render(**data)
