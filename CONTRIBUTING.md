# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

## Coding Standards

We follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html). Please ensure your code complies with this guide.

### Specific Requirements

If you are working with functions in the `nasem_equations` directory, please follow these additional guidelines:

1. **Single Return Value**: Each function should return only one value.
2. **Function Naming Convention**: The function name should follow the format `calculate_NAME`, where `NAME` is the name of the value being calculated.
3. **Assignment Before Return**: Assign the result of the calculation to a variable, and then return that variable. Do not return the calculation directly.
4. **Consistent Argument Names**: Ensure that the argument names exactly match the expected variable names used in the rest of the model.

### Pull Request Guidelines

Before you submit a pull request, ensure it meets the following guidelines:

1. The pull request should include additional tests if appropriate.
2. If the pull request adds functionality, the documentation should be updated.
3. The pull request must pass the testing workflow before it can be merged.
4. If new files for developers are added ensure they are included in the `dev` directory. 
Update the dev README.md to explain the addition. 

## Types of Contributions

### Report Bugs

If you find a bug, please report it by opening an issue on our [GitHub page](https://github.com/CNM-University-of-Guelph/NASEM-Model-Python). Please label the issue as "bug" and include the following information:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Feature Requests

If you have a feature request, please submit it as an issue on our [GitHub page](https://github.com/CNM-University-of-Guelph/NASEM-Model-Python). Label the issue as "enhancement" and provide a detailed explanation of how the feature would work. Keep the scope as narrow as possible to make it easier to implement.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Write Documentation

You can never have enough documentation! Please feel free to contribute to any part of the documentation, such as the official docs, docstrings, or even on the web in blog posts, articles, and such.

## Get Started!

Ready to contribute? Here's how to set up `nasem_dairy` for local development.

1. Download a copy of `nasem_dairy` locally.
2. Install `nasem_dairy` using `poetry`:

    ```console
    $ poetry install
    ```

3. Use `git` (or similar) to create a branch for local development and make your changes:

    ```console
    $ git checkout -b name-of-your-bugfix-or-feature
    ```

4. When you're done making changes, check that your changes conform to our coding standards (see below) and pass all tests.

5. Commit your changes and open a pull request on our [GitHub page](https://github.com/CNM-University-of-Guelph/NASEM-Model-Python).

6. Once a pull request is made a testing workflow will run. Your changes must pass all
of these tests before they can be merged into the main branch.

## Code of Conduct

Please note that the `nasem_dairy` project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.
