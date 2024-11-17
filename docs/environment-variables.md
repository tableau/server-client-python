---
title: Environment Variables
layout: docs
---

Tableau Server Client (TSC) can use environment variables to pull configuration
settings. This is a convenient way to manage the setting in one place and have
it used across all of the related calls.

## Supported environment variables

The following environment variables are supported by TSC:

Name | Description | Version | Default | Limit
:--- | :--- | :--- | :--- | :---
`TSC_CHUNK_SIZE_MB` | The size of chunks when uploading files. Limit is 64 MB. | 0.33 | 50 | 64
`TSC_PAGE_SIZE` | The number of items to return in a single page of results. | 0.33 | 100 | 1000
`TSC_FILESIZE_LIMIT_MB` | The maximum file size that can be uploaded. | 0.34 | 64 | 64

## Setting environment variables

To set an environment variable, you can use the `os` module in Python. Here is 
an example of setting the environment variables for the chunk size and page size:

```py
import os

import tableauserverclient as TSC

os.environ['TSC_CHUNK_SIZE_MB'] = '64'
os.environ['TSC_PAGE_SIZE'] = '1000'

# Continue with your TSC code
```

You can set these environment variables in your Python script, shell, IDE, bash
or PowerShell profile, CI/CD pipeline, .env file, or any other place where you
can set environment variables.

## Using environment variables

The TSC library will automatically pick up the environment variables when they
are set. If you set the environment variables in your Python script, they will
be used for the duration of the script. If you set them in your shell or IDE,
they will be used for all scripts that run in that environment.
