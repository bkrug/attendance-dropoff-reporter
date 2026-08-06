# Attendance Dropoff Reporter

Query Planning Center's API to detect members' whose attendence as dropped between an earlier and later 26-week period of time

## Planning Center

### GET requests

*List events within a group*

GUI for testing: https://api.planningcenteronline.com/explorer/groups/v2/groups/3017831/events?order=starts_at&filter=not_canceled&where[starts_at][gte]=2025-08-08&where[ends_at][lte]=2026-08-08
URL for program: https://api.planningcenteronline.com/groups/v2/groups/3017831/events?order=starts_at&filter=not_canceled&where[starts_at][gte]=2025-08-08&where[ends_at][lte]=2026-08-08

*List people within a group*

GUI for testing: https://api.planningcenteronline.com/explorer/groups/v2/groups/3017831/people
URL for program: https://api.planningcenteronline.com/groups/v2/groups/3017831/people

*Attendance of an event within the previously mentioned group*

GUI for testing: https://api.planningcenteronline.com/explorer/groups/v2/events/52089304/attendances
URL for program: https://api.planningcenteronline.com/groups/v2/events/52089304/attendances

### Authentication

https://api.planningcenteronline.com/docs/overview/authentication
https://api.planningcenteronline.com/oauth/applications
https://api.planningcenteronline.com/personal_access_tokens

### Filtering By Dates

https://api.planningcenteronline.com/docs/overview/dates-times

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