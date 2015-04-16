from chrome import panel

@panel("This is a dummy widget")
def render(request, session, config):
    return "hello world"
