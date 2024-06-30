Installing poetry
The latest installation method of poetry suggests using pipx, but then we typically use a conda env for package dev. So, poetry should be installed outside of the conda env for package dev, and then configured to use conda env path instead of the inbuilt venv:
```
poetry config virtualenvs.path $CONDA_ENV_PATH
```
Source: https://michhar.github.io/2023-07-poetry-with-conda/ 


Running `poetry install` from command line in the folder of this project will install a local version of the app inside of the current conda env.

The version number is important for when users install from github, as it tells them that it needs updating.
See https://nadeauinnovations.com/post/2023/01/easily-set-package-versions-with-git-tags-and-poetry-a-step-by-step-guide-for-python-developers/

So, to bump versions run `poetry version -h` for help, and run `poetry version minor` to increment from 0.1.0 to 0.20, for example.

Then, it's a good idea to tag it for github as well using `git tag 0.2.0` where the number matches the current version.

This needs to be pushed with `git push --tags` from terminal.


Installing a specific tag:
pip install git+https://github.com/CNM-University-of-Guelph/NASEM-Model-Python@v1.0.0a0