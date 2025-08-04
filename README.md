# NYU DevOps Shopcart Project

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![CI Build](https://github.com/CSCI-GA-2820-SU25-001/shopcarts/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU25-001/shopcarts/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU25-001/shopcarts/graph/badge.svg?token=FXUSYI35YL)](https://codecov.io/gh/CSCI-GA-2820-SU25-001/shopcarts)


## Overview

This project is a simple **Shopcarts Service** that lets customers save items they want to buy. This service has REST API's with all the basic features like adding, viewing, updating, or deleting both the cart and the items in it.


## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to fix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code
Pipfile             - Contains list of python runtime and development dependencies
k3d-config.yaml     - Configuration for K3D

k8s/                        - Kubernetes configuration files
├── deployment.yaml         - Defines the state for deploying pods
├── ingress.yaml            - Defines the routing paths for all hosts
└── service.yaml            - Define kubernetes services as needed

features/                   - Selenium UI based BDD testing files
├── environment.py          - Web browser environment config
├── shopcarts.feature       - Scenarios for BDD
└── steps
    ├── shopcarts_steps.py  - Steps file for shopcart.feature
    └── web_steps.py        - Gherkin langugage to web action translation

service/                    - service python package
├── __init__.py             - package initializer
├── config.py               - configuration parameters
├── models.py               - module with business models
├── routes.py               - module with service routes
├── common                  - common code package
├    ├── cli_commands.py    - Flask command to recreate all tables
├    ├── error_handlers.py  - HTTP error handling code
├    ├── log_handlers.py    - logging setup code
├    └── status.py          - HTTP status constants
└── static                  - common code package
    ├── index.html          - Admin UI page markup file
    ├── js                  - Contains Javascript code for UI
    ├── css                 - Contains style files for UI
    └── images              - Contains image assets used in UI

tests/                      - test cases package
├── __init__.py             - package initializer
├── factories.py            - Factory for testing with fake objects
├── test_cli_commands.py    - test suite for the CLI
├── test_models.py          - test suite for business models
└── test_routes.py          - test suite for service routes
```

## API Description:

The Shopcarts service has these API endpoints:

| Operation                         | Method | URL                                               |
|-----------------------------------|--------|---------------------------------------------------|
| **Health check endpoint**         | GET    | `/api/health`                                     |
| **Create a new shopcart**         | POST   | `/api/shopcarts`                                  |
| **Get a shopcart**                | GET    | `/api/shopcarts/{customer_id}`                    |
| **Query a shopcart**              | GET    | `/api/shopcarts/{customer_id}?max-price=`         |
| **List all shopcarts**            | GET    | `/api/shopcarts`                                  |
| **Update a shopcart**             | PUT    | `/api/shopcarts/{customer_id}`                    |
| **Delete a shopcart**             | DELETE | `/api/shopcarts/{customer_id}`                    |
| **Add an item to a shopcart**     | POST   | `/api/shopcarts/{customer_id}/items`              |
| **Get an item from a shopcart**   | GET    | `/api/shopcarts/{customer_id}/items/{product_id}` |
| **List all items in a shopcart**  | GET    | `/api/shopcarts/{customer_id}/items`              |
| **Update a shopcart item**        | PUT    | `/api/shopcarts/{customer_id}/items/{product_id}` |
| **Delete a shopcart item**        | DELETE | `/api/shopcarts/{customer_id}/items/{product_id}` |
| **Perform Action on shopcart**    | PUT    | `/api/shopcarts/{customer_id}/clear`              |

The UI for Admin is located at the `/` root URL.

## API Documentation

The documentation for the RESTful service can be found at:
``` /apidocs ```


## Commands for running tests and services.

### Running the Shopcart Service locally (`http://localhost:8080`):

```bash
honcho start
```
### Running the tests:
#### Run all unit tests locally
```bash
make test
```
#### BDD using Selenium
```bash
behave
```

### Docker and Kubernetes Deployment:

#### Build Docker Image
```bash
make build
```

#### Push to Registry
```bash
make push
```

#### Deploy to Kubernetes (local development)
```bash
make cluster      # Create a local K3D Kubernetes cluster
make deploy       # Deploy the service to Kubernetes
```

#### Clean Up
```bash
make clean        # Remove Docker build cache
make cluster-rm   # Delete the Kubernetes cluster
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
