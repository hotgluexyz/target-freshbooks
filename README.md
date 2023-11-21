# target-freshbooks

`target-freshbooks` is a Singer target for Freshbooks.

<!--

Developer TODO: Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPi repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

## Installation

Install from PyPi:

```bash
pipx install target-freshbooks
```

Install from GitHub:

```bash
pipx install git+https://github.com/ORG_NAME/target-freshbooks.git@main
```

-->

## Configuration


A full list of supported settings and capabilities for this
target is available by running:

```bash
target-freshbooks --about
```

### Configure using environment variables

This Singer target will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

<!--
Developer TODO: If your target requires special access on the destination system, or any special authentication requirements, provide those here.
-->

## Usage

You can easily run `target-freshbooks` by itself

### Executing the Target Directly

```bash
target-freshbooks --version
target-freshbooks --help
# Test using the "Carbon Intensity" sample:
tap-carbon-intensity | target-freshbooks --config /path/to/target-freshbooks-config.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `target-freshbooks` CLI interface directly using `poetry run`:

```bash
poetry run target-freshbooks --help
```
