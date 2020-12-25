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

Th module should be invocable from CLI, to enable handling large volumes of data.