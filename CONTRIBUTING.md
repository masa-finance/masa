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

1. **Adding new pages**:
   - Create a new `.rst` file in the `docs/source` directory.
   - Add the new page to the table of contents in `index.rst`.

2. **Updating existing pages**:
   - Find the relevant `.rst` file in `docs/source`.
   - Make your changes, following the existing style and structure.

3. **Docstrings**:
   - Use Google-style docstrings for Python code.
   - Ensure all parameters, return values, and exceptions are documented.

4. **Building docs**:
   - After making changes, rebuild the documentation:

     ```bash
     cd docs
     make html
     ```

   - Check the output in `docs/build/html` to ensure your changes appear correctly.

## Submitting Changes

1. Create a new branch for your changes.
2. Make your changes and commit them with a clear, descriptive commit message.
3. Push your branch and create a pull request.
4. In the pull request description, explain the changes you've made to the documentation.

Thank you for helping improve the MASA Project documentation!