#!/usr/bin/python3
import handlers


def routes_setup():
    return [
        (r'/data', handlers.Main),
        (r'/login', landlers.Login),
        (r'/login', landlers.Logout),
        ]
