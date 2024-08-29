# Changelog

<!--next-version-placeholder-->

## v0.1.0 (26/07/2023)

- First release of `nasem_dairy`!

## v1.0.0 - (29/08/2024)
### First Full Release
- First full release of the `nasem_dairy` package.
- Implemented all calculations in the NASEM 2021 Nutrient Requirements for Dairy Cattle.
- Set up continuous integration with GitHub Actions, including coverage reporting with Coveralls.
- Introduced comprehensive test suite across multiple operating systems and Python versions.
- Added `dag` subpackage for directed acyclic graph (DAG) representations of model equations.

### New Features
- Add the ModelOutput class for working with model results.
- Add demo scenarios through the `nd.demo` fucntion

### Improvements
- Improved documentation and added usage examples.

### Known Issues
- `graph-tool` dependency requires a Linux or macOS environment; not available on Windows.
