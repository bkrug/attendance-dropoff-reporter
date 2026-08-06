# Attendance Dropoff Reporter

Query Planning Center's API to detect members' whose attendence as dropped between an earlier and later 26-week period of time

## GET requests

*List events within a group*

GUI for testing: https://api.planningcenteronline.com/explorer/groups/v2/groups/3017831/events?filter=not_canceled
URL for program: https://api.planningcenteronline.com/groups/v2/groups/3017831/events?filter=not_canceled

*List people within a group*

GUI for testing: https://api.planningcenteronline.com/explorer/groups/v2/groups/3017831/people
URL for program: https://api.planningcenteronline.com/groups/v2/groups/3017831/people

## Learning Python

### Installing pipenv in Fedora

```
sudo dnf install pipx
pipx install pipenv
```

### Warning messages in import statements

If we get warning messages in an import statement despite having already installed a library to our Pipfile,
use this command: `pipenv --venv` to find the path to an interpreter.
In VS Code, press CTRL+SHIFT+P, and run "Python: Select Interpreter" and enter the path that was output by the previous command.