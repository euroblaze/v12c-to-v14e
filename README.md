### What should this module do?

This module can be used as a basis tool for to migrate v12c to v12e.

### How does it execute?

`run.py` is a wrapper that 

- Establishes the sequence of execution
- Performs sanity checks on input data
- Provides logging calls
- Foresees as many problems as possible, and establishes call-paths to log & ignore the failure and continue execution.
- Breaks the execution in fatal conditions


Following modules can be migrated using this migration package:

- Contacts
- CRM
- Sales
- Invoice
- Projects
- Recruitment

It can be used in the multicompany context.

### Partial & Total Execution

Data from all modules do not have to be migrated at once. 
It is possible to migrate specific datasets, including the required dependencies

### CLI Invocation

1. This migration-module should be invocable from CLI, to enable handling large volumes of data.
Executing from web-browser is ruled out.

2. Parts of the module can be cronned to execute automatically, periodically.

3. `run.py` can accept sysargs/parameters for selective execution.

### Necessary improvements


2. Comments & log messages only in English.
3. Move hardcoded auth-credentials into a single config file.