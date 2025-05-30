Contribute
==========

.. _contribute:

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

Coding Standards
----------------

We follow the `Google Python Style Guide <https://google.github.io/styleguide/pyguide.html>`_. Please ensure your code complies with this guide.

NASEM Equations Requirements
----------------------------

If you are working with functions in the *nasem_equations* directory, please follow these additional guidelines:

1. **Single Return Value**: Each function should return only one value.
2. **Function Naming Convention**: The function name should follow the format *calculate_NAME*, where *NAME* is the name of the value being calculated.
3. **Assignment Before Return**: Assign the result of the calculation to a variable, and then return that variable. Do not return the calculation directly.
4. **Consistent Argument Names**: Ensure that the argument names exactly match the expected variable names used in the rest of the model.

Pull Request Guidelines
-----------------------

Before you submit a pull request, ensure it meets the following guidelines:

1. The pull request should include additional tests if appropriate.
2. If the pull request adds functionality, the documentation should be updated.
3. The pull request must pass the testing workflow before it can be merged.
4. If new files for developers are added ensure they are included in the *dev* directory. Update the dev README.md to explain the addition. 

Features and Bugfixes
---------------------

If you find a bug or have a feature request please open a new issue on our `GitHub page <https://github.com/CNM-University-of-Guelph/NASEM-Model-Python>`_.
Select the appropriate template and fill in the required information.


Getting Started
---------------

Ready to contribute? Here's how to set up ``nasem_dairy`` for local development.

1. Download a copy of ``nasem_dairy`` locally.
2. Install ``nasem_dairy`` using ``poetry``:

    .. code-block:: console

        poetry install

3. Use ``git`` to create a branch for local development and make your changes:

    .. code-block:: console

        git checkout -b name-of-your-feature

4. When you're done making changes, check that your changes conform to our coding standards and pass all tests.

5. Commit your changes and open a pull request on our `GitHub page <https://github.com/CNM-University-of-Guelph/NASEM-Model-Python>`_.

6. Once a pull request is made a testing workflow will run. Your changes must pass all of these tests before they can be merged into the main branch.

Code of Conduct
---------------

Please note that the `nasem_dairy` project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.