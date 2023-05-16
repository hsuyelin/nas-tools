# Maintainers Guide

This document describes tools, tasks and workflow that one needs to be familiar with in order to effectively maintain
this project. If you use this package within your own software as is but don't plan on modifying it, this guide is
**not** for you.

## Tools

### Python (and friends)

We recommend using [pyenv](https://github.com/pyenv/pyenv) for Python runtime management. If you use macOS, follow the following steps:

```bash
$ brew update
$ brew install pyenv
```

Install necessary Python runtimes for development/testing. You can rely on Travis CI builds for testing with various major versions. https://github.com/slackapi/bolt-python/blob/main/.travis.yml

```bash
$ pyenv install -l | grep -v "-e[conda|stackless|pypy]"

$ pyenv install 3.8.5 # select the latest patch version
$ pyenv local 3.8.5

$ pyenv versions
  system
  3.6.10
  3.7.7
* 3.8.5 (set by /path-to-bolt-python/.python-version)

$ pyenv rehash
```

Then, you can create a new Virtual Environment this way:

```
$ python -m venv env_3.8.5
$ source env_3.8.5/bin/activate
```

## Tasks

### Testing

#### Run All the Unit Tests

If you make some changes to this SDK, please write corresponding unit tests as much as possible. You can easily run all the tests by running the following script.

If this is your first time to run tests, although it may take a bit long time, running the following script is the easiest.

```bash
$ ./scripts/install_all_and_run_tests.sh
```

Once you installed all the required dependencies, you can use the following one.

```bash
$ ./scripts/run_tests.sh
```

Also, you can run a single test this way.

```bash
$ ./scripts/run_tests.sh tests/scenario_tests/test_app.py
```

#### Run the Samples

If you make changes to `slack_bolt/adapter/*`, please verify if it surely works by running the apps under `examples` directory.

```bash
# Install all optional dependencies
$ pip install -e ".[adapter]"
$ pip install -e ".[adapter_testing]"

# Set required env variables
$ export SLACK_SIGNING_SECRET=***
$ export SLACK_BOT_TOKEN=xoxb-***

# Standalone apps
$ cd examples/
$ python app.py
$ python async_app.py

# Flask apps
$ cd examples/flask
$ FLASK_APP=app.py FLASK_ENV=development flask run -p 3000

# In another terminal
$ ngrok http 3000 --subdomain {your-domain}
```

#### Develop Locally

If you want to test the package locally you can.
1. Build the package locally
   - Run 
     ```bash
     scripts/build_pypi_package.sh
     ```
   - This will create a `.whl` file in the `./dist` folder
2. Use the built package
   - Example `/dist/slack_bolt-1.2.3-py2.py3-none-any.whl` was created
   - From anywhere on your machine you can install this package to a project with 
     ```bash
     pip install <project path>/dist/slack_bolt-1.2.3-py2.py3-none-any.whl
     ```
   - It is also possible to include `<project path>/dist/slack_bolt-1.2.3-py2.py3-none-any.whl` in a [requirements.txt](https://pip.pypa.io/en/stable/user_guide/#requirements-files) file 


### Releasing

#### Generate API documents

```bash
./scripts/generate_api_docs.sh
```

#### test.pypi.org deployment

##### $HOME/.pypirc

```
[testpypi]
username: {your username}
password: {your password}
```


#### Development Deployment

1. Create a branch in which the development release will live:
    - Bump the version number in adherence to [Semantic Versioning](http://semver.org/) and [Developmental Release](https://peps.python.org/pep-0440/#developmental-releases) in `slack_bolt/version.py`
      - Example the current version is `1.2.3` a proper development bump would be `1.3.0.dev0`
      - `.dev` will indicate to pip that this is a [Development Release](https://peps.python.org/pep-0440/#developmental-releases) 
      - Note that the `dev` version can be bumped in development releases: `1.3.0.dev0` -> `1.3.0.dev1`
    - Commit with a message including the new version number. For example `1.3.0.dev0` & Push the commit to a branch where the development release will live (create it if it does not exist)
      - `git checkout -b future-release`
      - `git commit -m 'version 1.3.0.dev0'`
      - `git push future-release`
    - Create a git tag for the release. For example `git tag v1.3.0.dev0`.
    - Push the tag up to github with `git push origin --tags`

2. Distribute the release
   - Use the latest stable Python runtime
   - `python -m venv .venv`
   - `./scripts/deploy_to_pypi_org.sh`
   - You do not need to create a GitHub release

3. (Slack Internal) Communicate the release internally


#### Production Deployment

1. Create the commit for the release: 
   - Bump the version number in adherence to [Semantic Versioning](http://semver.org/) in `slack_bolt/version.py`
   - Commit with a message including the new version number. For example `1.2.3` & Push the commit to a branch and create a PR to sanity check.
     - `git checkout -b v1.2.3-release`
     - `git commit -m 'version 1.2.3'`
     - `git push {your-fork} v1.2.3-release`
   - Merge in release PR after getting an approval from at least one maintainer.
   - Create a git tag for the release. For example `git tag v1.2.3`.
   - Push the tag up to github with `git push origin --tags`

2. Distribute the release
   - Use the latest stable Python runtime
   - `python -m venv .venv`
   - `./scripts/deploy_to_pypi_org.sh`
   - Create a GitHub release - https://github.com/slackapi/bolt-python/releases

   ```markdown
   ## New Features

   ### Awesome Feature 1

   Description here.

   ### Awesome Feature 2

   Description here.

   ## Changes

   * #123 Make it better - thanks @SlackHQ
   * #123 Fix something wrong - thanks @seratch
   ```

3. (Slack Internal) Communicate the release internally
   - Include a link to the GitHub release

4. Make announcements
   - #tools-bolt in community.slack.com

5. (Slack Internal) Tweet by @SlackAPI
   - Not necessary for patch updates, might be needed for minor updates, definitely needed for major updates. Include a link to the GitHub release

## Workflow

### Versioning and Tags

This project uses semantic versioning, expressed through the numbering scheme of
[PEP-0440](https://www.python.org/dev/peps/pep-0440/).

### Branches

`main` is where active development occurs. Long running named feature branches are occasionally created for
collaboration on a feature that has a large scope (because everyone cannot push commits to another person's open Pull
Request). At some point in the future after a major version increment, there may be maintenance branches for older major
versions.

### Issue Management

Labels are used to run issues through an organized workflow. Here are the basic definitions:

- `bug`: A confirmed bug report. A bug is considered confirmed when reproduction steps have been
  documented and the issue has been reproduced.
- `enhancement`: A feature request for something this package might not already do.
- `docs`: An issue that is purely about documentation work.
- `tests`: An issue that is purely about testing work.
- `discussion`: An issue that is purely meant to hold a discussion. Typically the maintainers are looking for feedback in this issues.
- `question`: An issue that is like a support request because the user's usage was not correct.

**Triage** is the process of taking new issues that aren't yet "seen" and marking them with a basic level of information
with labels. An issue should have **one** of the following labels applied: `bug`, `enhancement`, `question`,
`needs feedback`, `docs`, `tests`, or `discussion`.

Issues are closed when a resolution has been reached. If for any reason a closed issue seems relevant once again,
reopening is great and better than creating a duplicate issue.

## Everything else

When in doubt, find the other maintainers and ask.
