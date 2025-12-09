"""
GitHub API integration for PR analysis.
"""

import os
import httpx


async def get_pr_diff(repo: str, pr_number: int) -> str:
    """
    Fetch Pull Request diff from GitHub.

    Args:
        repo: Repository in format 'owner/repo'
        pr_number: Pull request number

    Returns:
        PR diff as string
    """
    try:
        # GitHub API endpoint
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

        # Get GitHub token from environment if available
        headers = {
            "Accept": "application/vnd.github.v3.diff",
        }

        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"

        # Fetch PR diff
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)

            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                return f"Error: PR #{pr_number} not found in {repo}"
            elif response.status_code == 403:
                return "Error: Rate limit exceeded or authentication required. Set GITHUB_TOKEN environment variable."
            else:
                return f"Error: GitHub API returned status {response.status_code}"

    except httpx.TimeoutException:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error fetching PR diff: {str(e)}"
