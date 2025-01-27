# Contribution Guide

Thank you for your interest in contributing to OpenHosta! We appreciate community contributions and are excited to collaborate with you to improve this project.

All types of contributions are encouraged and valued. See the Table of Contents for different ways to help and details about how this project handles them. Please make sure to read the relevant section before making your contribution.

> And if you like the project, but just don't have time to contribute, that's fine. There are other easy ways to support the project and show your appreciation, which we would also be very happy about:
> - Star the project
> - Tweet about it
> - Refer this project in your project's readme
> - Mention the project at local meetups and tell your friends/colleagues

### Table of Content

- [Contribution Guide](#contribution-guide)
    - [Table of Content](#table-of-content)
  - [How to Contribute](#how-to-contribute)
    - [Reporting Bugs](#reporting-bugs)
    - [Suggesting Enhancements](#suggesting-enhancements)
    - [Submitting Changes](#submitting-changes)
  - [Style Guide](#style-guide)
    - [Code Review](#code-review)
    - [Coding Style](#coding-style)
    - [Documentation](#documentation)
  - [Delivery Method](#delivery-method)
    - [Pre-release checks](#pre-release-checks)
    - [Release process](#release-process)
    - [Post-release tasks](#post-release-tasks)
  - [Conclusion](#conclusion)
    - [Additional Information](#additional-information)

---

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on our [GitHub repository](https://github.com/hand-e-fr/OpenHosta-dev/issues) and include as many details as possible. Please provide the following information:

- A clear and concise description of the bug.
- Steps to reproduce the bug.
- The version of Python and dependencies used.
- Any other relevant information (logs, screenshots, etc.).

### Suggesting Enhancements

We welcome enhancement suggestions. If you have an idea to improve OpenHosta, please open an issue on our [GitHub repository](https://github.com/hand-e-fr/OpenHosta-dev/issues) and describe your suggestion in detail. Please include:

- A clear and concise description of the proposed enhancement.
- Reasons why you believe this enhancement is necessary.
- Any other relevant information (code examples, links to other projects, etc.).

### Submitting Changes

If you wish to make changes to the code, please follow these steps:

1. **Fork the Repository**: Click the "Fork" button at the top of the page to create a copy of this repository on your GitHub account.

2. **Clone Your Fork**: Clone your fork locally using the following command:
    ```sh
    git clone https://github.com/hand-e-fr/OpenHosta.git
    ```

3. **Create a Branch**: Create a new branch for your feature or bug fix:
    ```sh
    git checkout -b my-new-feature
    ```

4. **Make Your Changes**: Make the necessary changes in your preferred code editor.

5. **Commit Your Changes**: Add and commit your changes with clear and descriptive commit messages:
    ```sh
    git add .
    git commit -m "Add my new feature"
    ```

6. **Push Your Branch**: Push your branch to your GitHub fork:
    ```sh
    git push origin my-new-feature
    ```

7. **Open a Pull Request**: Go to the original repository and open a Pull Request from your fork. Describe the changes you have made and why they are necessary.

---

## Style Guide

### Code Review

All contributions will undergo a code review by the project maintainers. Please be patient while we review your Pull Request. We may request changes before merging your contribution.

### Coding Style

Please ensure that your code follows the project's style conventions. We use `black` as the style guide for Python. You can use tools like `flake8` to check that your code adheres to these conventions.

### Documentation

If you add a new feature, please update the documentation accordingly. The documentation should be clear, concise, and include usage examples.

## Delivery Method

### Pre-release checks

   1. Merge all concerned branches into `dev`
   2. Verify that all quality checks pass successfully
   3. Perform a thorough code review using `git diff`
   4. Ensure the CHANGELOG.md is up to date
   5. Review the documentation for accuracy
   6. Verify all unit tests are passing
   7. Confirm all version numbers have been properly updated
      - pyproject.toml: version = "X.Y.patch"
      - README.md: vX.Y.patch - Open-Source Project
      - docs/doc.md: Documentation for version: **X.Y.patch**
      - src/OpenHosta/__init__.py: __version__ = "X.Y.patch"
   8. Conduct bug hunting on a clean virtual environment and perform user testing

### Release process

   1. Merge `dev` branch into `main`
   2. Draft a new release on GitHub
   3. Copy the changelog entries to the release notes section
   4. Add any additional release notes if necessary
   5. Push the package to PyPI (automatically via GitHub Actions)
   6. Send release announcement on Discord

### Post-release tasks

   1. Update all other branches with the new release
   2. Review and update issues as needed
   3. Create a new milestone for the next release

---

## Conclusion

### Additional Information
We have adopted a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a respectful and inclusive environment for all contributors. Please take a moment to read it before you start contributing.

If you have any questions or need further assistance, feel free to contact us at: support@openhosta.com.

---

Thank you again for your interest in contributing to OpenHosta!

**The OpenHosta Team**