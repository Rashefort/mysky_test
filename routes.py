#!/usr/bin/python3
import handlers


def routes_setup():
    return [
        (r'/post', handlers.PostFile),
        (r'/login', handlers.Login),
        (r'/logout', handlers.Logout),
        (r'/', handlers.Main),
        (r'/pdf/(.+)', handlers.Preview),
        ]
