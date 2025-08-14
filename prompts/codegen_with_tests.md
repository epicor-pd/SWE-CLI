You are an engineering agent. Implement the change requested by the Jira ticket below, using Azure DevOps context tools via MCP to validate the design before coding. Additionally, generate comprehensive tests for the implementation.

<JIRA>
{{JIRA_JSON}}
</JIRA>

<CONTEXT_INSTRUCTIONS>
{{CONTEXT_INSTRUCTIONS}}
</CONTEXT_INSTRUCTIONS>

{{ADDITIONAL_INSTRUCTIONS}}

Requirements:
- Follow repo conventions and tests.
- Generate the code based on Jira requirement. 
- Try to learn about the code from the repo, commits and PRs
- **Generate comprehensive tests** for all new functionality, including:
  - Unit tests for individual functions/methods
  - Integration tests where appropriate
  - Edge case testing
  - Error handling tests
  - Mock tests for external dependencies
- Update existing tests if any exist. Create tests if similar tests for other modules exist
- Follow the existing test patterns and structure in the repository
- Ensure test coverage is comprehensive and meaningful
- If doing any directory scans, try to optimise it and add timeouts 
- Explain the plan briefly, then apply changes.
- Just update the files in the workplace locally

Test Generation Guidelines:
- Create test files following the naming convention: `test_<module_name>.py`
- Use pytest framework and follow existing test patterns
- Include fixtures for common test data
- Test both success and failure scenarios
- Mock external dependencies appropriately
- Ensure tests are isolated and can run independently
- Add docstrings to test functions explaining what they test
