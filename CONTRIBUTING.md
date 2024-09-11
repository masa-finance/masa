# Contributing to MASA Project

Thank you for your interest in contributing to the MASA Project! This guide will help you understand our documentation best practices and how to contribute effectively.

## Documentation Best Practices

1. **Keep it up to date**: Always update the documentation when you make changes to the code.

2. **Use clear and concise language**: Write in simple, easy-to-understand terms.

3. **Provide examples**: Include code snippets and usage examples where appropriate.

4. **Follow the structure**: Maintain the existing documentation structure for consistency.

5. **Use proper formatting**: Utilize Markdown for README.md and reStructuredText for Sphinx documentation.

6. **Document all public APIs**: Ensure all public functions, classes, and modules have docstrings.

7. **Cross-reference**: Link related sections of the documentation where relevant.

8. **Test your documentation**: Ensure code examples work and instructions are accurate.

## Updating Documentation

### README.md

- Keep it concise and focused on getting users started quickly.
- Update the quick start guide if installation or basic usage changes.
- Ensure links to full documentation are correct.

### Sphinx Documentation

1. **Updating existing pages**:
   - Find the relevant `.rst` file in `docs/source`.
   - Make your changes, following the existing style and structure.

2. **Adding new pages**:
   - Create a new `.rst` file in the `docs/source` directory.
   - Add the new page to the table of contents in `index.rst`.

3. **Docstrings**:
   - Use Google-style docstrings for Python code.
   - Ensure all parameters, return values, and exceptions are documented.

4. **Viewing updated documentation**:
   - The documentation is automatically rebuilt when viewed using the CLI command:
     ```
     masa-cli --docs [page_name]
     ```
   - This command will rebuild the docs and open them in your default web browser.

5. **Manual rebuilding (if necessary)**:
   - Navigate to the `docs` directory.
   - Run:
     ```
     python update_docs.py
     ```
   - The built HTML will be in `docs/build/html`.

Remember, you don't need to manually build the documentation for normal development work, as it's automatically rebuilt when viewed through the CLI.

## Submitting Changes

1. Create a new branch for your changes.
2. Make your changes and commit them with a clear, descriptive commit message.
3. Push your branch and create a pull request.
4. In the pull request description, explain the changes you've made to the code and documentation.

## Code Style

- Follow PEP 8 guidelines for Python code.
- Use meaningful variable and function names.
- Keep functions small and focused on a single task.
- Write unit tests for new functionality.

## Reporting Issues

- Use the GitHub issue tracker to report bugs or suggest enhancements.
- Provide a clear description of the issue or enhancement.
- Include steps to reproduce for bugs, and use case scenarios for enhancements.

Thank you for helping improve the MASA Project! Your contributions are valued and appreciated.