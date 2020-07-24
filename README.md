# dnf-plugin-rkhunter
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Description
Automatic updates of rkhunter property files after DNF transactions.
RPM spec file available [here](https://fedorapeople.org/cgit/keesdejong/public_git/rpmbuild.git/tree/SPECS/dnf-plugin-rkhunter.spec).

## Documentation
In the cloned git directory, run `man man/dnf-plugin-rkhunter.8` to see the documentation.

## Discontinued
I created this plugin to learn a bit more about DNF plugins. Best solution is to use the `dnf-plugin-post-transaction-actions` plugin and created the following configuration in /etc/dnf/plugins/post-transaction-actions.d/rkhunter.action: `*:any:rkhunter --propupd`.
