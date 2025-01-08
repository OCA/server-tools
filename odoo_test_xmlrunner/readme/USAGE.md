
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

permissions:
    contents: read
    checks: write
    id-token: write

on:
  push:
    branches: ["main"]
    tags: ["*"]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-22.04
    container: ${{ matrix.container }}
    name: ${{ matrix.name }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - container: ghcr.io/oca/oca-ci/py3.10-odoo17.0:latest
            name: test with Odoo
    services:
      postgres:
        image: postgres:12.0
        env:
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
          POSTGRES_DB: odoo
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v3
        with:
          persist-credentials: false
      - name: Install addons and dependencies
        run: oca_install_addons
      - name: Check licenses
        run: manifestoo -d . check-licenses
      - name: Check development status
        run: manifestoo -d . check-dev-status --default-dev-status=Beta
      - name: Initialize test db
        run: oca_init_test_database
      - name: Run tests
        run: oca_run_tests
      - uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
      - name: Publish Test Report
        uses: mikepenz/action-junit-report@v4
        if: success() || failure() # always run even if the previous step fails
        with:
          report_paths: 'test_results/*.xml'

```