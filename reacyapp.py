from flask import Flask
from reactpy.backend.flask import configure

from reactpy import component, html, run, hooks

'''TODO set state to change page using react hook'''
@component
def App():
    page = 'findDorm'
    if page == 'findDorm':
        return findDormPage()
    elif page == 'findMate':
        return findMatePage()
    elif page == 'matched':
        return matchedPage()
    

@component
def findDormPage():
    return html._(
        html.h1("findDormPage"),
        html.img({"src": "https://picsum.photos/id/0/500/300"}),
        html.ul(html.li("The first thing I need to do is...")),
    )

@component
def findMatePage():
    return html._(
        html.h1("findMatePage"),
    )

@component
def matchedPage():
    return html._(
        html.h1("matched"),
        html.img({"src": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/RedCat_8727.jpg/1200px-RedCat_8727.jpg"}),
        html.ul(html.li("The first thing I need to do is...")),
    )

run(App)



