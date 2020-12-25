### What should this module do?

This module can be used as a basis tool for to migrate v12c to v12e.

### How does it execute?

`run.py` is a wrapper that 

- Establishes the sequence of execution
- Performs sanity checks on input data
- Provides logging calls
- Foresees as many problems as possible, and establishes call-paths to log & ignore the failure and continue execution.
- Breaks the execution in fatal conditions


Following modules are migrated:

- Contacts
- CRM
- Sales
- Invoice
- Projects
- Recruitment

It can be used in the multicompany context.

### Necessary improvements

1. This module should be invocable from CLI, to enable handling large volumes of data.
Executing from web-browser is ruled out.
2. Comments & log messages only in English.
3. Move hardcoded auth-credentials into a single config file.