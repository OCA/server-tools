
## Run the native Odoo tests

Run the native Odoo tests. See the [Odoo documentation](https://www.odoo.com/documentation/17.0/fr/developer/reference/backend/testing.html) for more information.

### Gitlab CI usage example

Add the following job to your `.gitlab-ci.yml` file:

```yaml

stages:
  - test

variables:
  POSTGRES_DB: odoo
  POSTGRES_USER: odoo
  POSTGRES_PASSWORD: odoo
  POSTGRES_HOST_AUTH_METHOD: trust

test:
  stage: test
  image:
    name: ghcr.io/oca/oca-ci/py3.10-odoo17.0:latest
  services:
    - name: postgres:15
  tags:
    - gitlab-org-docker
  script:
    # install odoo and run tests
    - oca_install_addons && oca_init_test_database && oca_run_tests
    # generate coverage report
    - coverage html -d htmlcov && coverage xml -o coverage.xml
    # read line-rate from coverage.xml and print it as percentage
    - total=$(grep -oP '<coverage[^>]*line-rate="\K[0-9.]+' coverage.xml | head -n 1 | awk '{print $1 * 100}') && echo "total ${total}%"
  coverage: '/(?i)total.*? (100(?:\.0+)?\%|[1-9]?\d(?:\.\d+)?\%)$/'
  artifacts:
    paths:
      - htmlcov/*
    when: always
    reports:
      junit: test_results/*.xml
      coverage_report:
          coverage_format: cobertura
          path: coverage.xml
```
### Github Actions usage example

Add the following job to your `.github/workflows/main.yml` file:

```yaml
name: tests

on:
  pull_request:
  push:

jobs:
  test:
    runs-on: ubuntu-22.04
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
          POSTGRES_DB: odoo
        ports:
          - 5432:5432
    env:
      DB: odoo
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: odoo --load=odoo_test_xmlrunner -i my_module --test-enable --stop-after-init
      - name: Publish test report
        uses: mikepenz/action-junit-report@v4
        if: success() || failure()
        with:
          report_paths: test_results/*.xml

```
