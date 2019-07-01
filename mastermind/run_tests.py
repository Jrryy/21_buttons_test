#!/usr/bin/env python
"""
Script to compute the project's full coverage.-
"""

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    from coverage import Coverage

    cov = Coverage(omit=['*/tests.py', '*/migrations/*', '*/__init__.py', '*/admin.py'])
    cov.set_option('report:show_missing', True)
    cov.erase()
    cov.start()

    execute_from_command_line(['manage.py', 'test', '-v2'])

    cov.stop()
    cov.save()
    cov.report()
