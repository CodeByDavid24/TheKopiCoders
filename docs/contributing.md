# Contributing to SootheAI

Thank you for your interest in contributing to SootheAI! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and considerate of different viewpoints and experiences
- Use welcoming and inclusive language
- Focus on constructive feedback and collaborative problem-solving
- Show empathy towards other community members

## Getting Started

### Find an Issue

- Check the [Issues](https://github.com/yourusername/soothe_app/issues) page for tasks labeled "good first issue"
- Look for issues that match your skills and interests
- Comment on an issue to express your interest before starting work

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/soothe_app.git
   cd soothe_app
   ```
3. Add the original repository as an upstream remote:
   ```bash
   git remote add upstream https://github.com/originalowner/soothe_app.git
   ```

### Set Up Development Environment

Follow the instructions in the [Development Guide](development.md) to set up your development environment.

## Development Workflow

### Create a Branch

Create a branch with a descriptive name for your changes:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-you-are-fixing
```

### Make Changes

1. Make your code changes following the [coding standards](development.md#coding-standards)
2. Write or update tests as needed
3. Run tests locally to ensure they pass:
   ```bash
   python test_runner.py
   ```
4. Ensure your code is properly formatted:
   ```bash
   black src tests
   flake8 src tests
   ```

### Commit Your Changes

1. Use clear, descriptive commit messages
2. Reference issue numbers in your commit messages:
   ```
   git commit -m "Add feature X (fixes #123)"
   ```
3. Keep commits focused and atomic

### Push and Create a Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Create a pull request from your branch to the main repository's `develop` branch
3. Fill out the pull request template with details about your changes

## Pull Request Guidelines

### PR Description

Provide a detailed description of your changes, including:

- What problem this PR solves
- How the changes address the problem
- Any potential side effects or areas that need special attention
- Screenshots or GIFs for UI changes (if applicable)

### PR Requirements

- All tests must pass
- New code must include tests
- Code must follow project style guidelines
- Documentation must be updated as needed

### Review Process

1. At least one maintainer will review your PR
2. Automated tests will run on your PR
3. You may be asked to make changes or address feedback
4. Once approved, a maintainer will merge your PR

## Types of Contributions

### Code Contributions

- Bug fixes
- New features
- Performance improvements
- Code refactoring

### Documentation Contributions

- Improving README and other documentation files
- Adding code comments
- Creating examples and tutorials
- Fixing typos and clarifying existing documentation

### Content Contributions

- Character definitions
- Story milestones and narrative elements
- Educational content about anxiety and mental health

### Testing Contributions

- Writing new tests
- Improving existing tests
- Manual testing and bug reporting

## Special Guidelines for Mental Health Content

As SootheAI deals with mental health topics, please follow these additional guidelines:

1. **Accuracy**: Ensure any mental health information is accurate and evidence-based
2. **Sensitivity**: Use respectful, non-stigmatizing language when discussing mental health
3. **No Diagnosis**: Avoid content that could be construed as medical advice or diagnosis
4. **Safety First**: Always prioritize user safety in any content related to mental health
5. **Resources**: Include appropriate support resources when relevant

## Reporting Bugs

If you find a bug, please report it by opening an issue that includes:

1. A clear, descriptive title
2. Detailed steps to reproduce the bug
3. Expected behavior vs. actual behavior
4. Any error messages or logs
5. Your environment (OS, Python version, etc.)
6. Screenshots if applicable

## Suggesting Features

Feature suggestions are welcome! Please:

1. Check if the feature has already been suggested or implemented
2. Open an issue with a clear, descriptive title
3. Provide a detailed description of the feature
4. Explain the benefit to users
5. Include mockups or examples if applicable

## Code Review Guidelines

When reviewing PRs, consider:

- Does the code follow project standards?
- Are there sufficient tests?
- Is the documentation clear and complete?
- Does the PR address a real need?
- Is there a simpler or more maintainable solution?
- Provide constructive, specific feedback
- Acknowledge good work!

## Attribution

Contributors will be acknowledged in:

- The project's CONTRIBUTORS.md file
- Release notes for significant contributions
- Project documentation where appropriate

## Getting Help

If you need help with your contribution:

- Ask in the original issue thread
- Reach out to project maintainers
- Check the project documentation
- Review existing code for examples

We appreciate your contributions and look forward to your involvement in making SootheAI better!
