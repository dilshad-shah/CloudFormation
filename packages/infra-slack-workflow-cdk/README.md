# Infra Slack Workflow CDK

Repository for handling #cloud-infra Slack workflow requests.

## Setup

- `asdf install` reads `.tool-versions` and installs each of the tools there
- `pnpm install` reads `package.json` and `pnpm-lock.yaml` and installs all depedencies

## Useful commands

- `pnpm build` compile typescript to js
- `pnpm test` perform the jest unit tests
- `pnpm lint` run linting toosl like eslint and prettier
- `pnpm fix` automatically fix issues that linting finds
- `pnpm clean` clear output directories and start clean

## CDK version dependency issues

The CDK is split across many packages, one for each AWS service they represent. Despite being published separately,
each package is tightly coupled to core packages for base classes. That means all packages must be on the exact same
version the whole way down the dependency tree.

To make matters worse, the AWS dev team does not strictly follow semver on their releases. Minor (1.x.0) version changes
can include breaking changes. They use a stable/experimental flag per package to communicate which ones will likely have
breaking changes. It's still best to upgrade to the latest and work through these changes if possible.

Problems can arise when libraries are used (which this repo does) because they also depend on those same CDK packages.
Resolution of a dependency's dependencies (transitive) happens when you install/upgrade it and then are stored in the
lock file. That means if you install package A today and package B tomorrow, you can wind up with CDK package versions
that don't agree.

There are a couple ways to fix this:

1. `pnpm upgrade -i` to see all direct dependencies that have an update available. Select all CDK packages and libraries
   and update them together. This should be the main method for normal use cases, fixing breaking changes as you go.

2. If you're in a situation where you cannot overcome those breaking changes at the time, you can use a pnpm feature to
   force the version to resolve to the same across all packages. There is a [.pnpmfile.cjs](.pnpmfile.cjs) included in this
   repo for you to use, if needed. Its use is explained [here](https://pnpm.io/pnpmfile). It effectively works the
   same as [yarn resolutions](https://classic.yarnpkg.com/en/docs/selective-version-resolutions/).
