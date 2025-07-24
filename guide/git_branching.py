#!/usr/bin/env python3
"""
Git Branching Strategy Implementation

This module provides utilities and best practices for implementing a consistent Git branching strategy.
It enforces a structured workflow that improves collaboration and maintains a clean project history.

Key benefits of a consistent branching strategy:
- Clear separation between production, development, and feature work
- Easier collaboration among team members
- Cleaner project history with meaningful commits
- Safer deployment process with reduced risk of issues in production
"""

from dataclasses import dataclass
import subprocess
import sys
from typing import Optional, List
from datetime import datetime


@dataclass
class BranchingStrategy:
    """
    Represents a Git branching strategy based on the widely-adopted GitFlow approach.
    
    This strategy defines how branches should be named and managed throughout the
    development lifecycle. Following this approach provides several benefits:
    
    - Isolates new development from production code
    - Enables parallel development by multiple team members
    - Organizes branches by purpose (features, bugfixes, hotfixes)
    - Maintains a clean and meaningful commit history
    """
    main_branch: str
    development_branch: str
    feature_prefix: str
    bugfix_prefix: str
    hotfix_prefix: str
    
    @classmethod
    def default_strategy(cls) -> "BranchingStrategy":
        """
        Returns the recommended default branching strategy.
        
        Main branch (main): 
        - Contains production-ready code
        - Should always be deployable
        - Never commit directly to this branch
        
        Development branch (dev):
        - Contains code in active development for the next release
        - Features are merged here first for integration testing
        
        Feature branches (feature/*):
        - Created from the development branch
        - Used for developing new features
        - Merged back into development when complete
        
        Bugfix branches (bugfix/*):
        - Created from the main branch
        - Used for fixing issues in production
        - Merged to both main and development branches
        
        Hotfix branches (hotfix/*):
        - Used for critical production fixes
        - Created from main, merged to both main and development
        """
        return cls(
            main_branch="main",
            development_branch="dev",
            feature_prefix="feature/",
            bugfix_prefix="bugfix/",
            hotfix_prefix="hotfix/"
        )


class GitBranching:
    """
    Utility class for Git branch management following best practices.
    
    This class provides methods to create and manage branches according to a 
    consistent branching strategy. It enforces workflows that help maintain 
    a clean repository history and facilitate collaborative development.
    
    Best practices enforced:
    1. Feature branches always derive from development branch
    2. Bugfix branches always derive from main branch
    3. Hotfix branches always derive from main branch
    4. Non-fast-forward merges to preserve branch history
    5. Validation of branch existence before operations
    """
    
    def __init__(self, strategy: Optional[BranchingStrategy] = None):
        """
        Initialize with a branching strategy, or use the default.
        
        Args:
            strategy: Custom branching strategy configuration. If None, uses the default.
        """
        self.strategy = strategy or BranchingStrategy.default_strategy()
        print(f"🔄 Initialized Git branching with strategy:")
        print(f"  • Main branch: {self.strategy.main_branch}")
        print(f"  • Development branch: {self.strategy.development_branch}")
        print(f"  • Feature branches: {self.strategy.feature_prefix}*")
        print(f"  • Bugfix branches: {self.strategy.bugfix_prefix}*")
        print(f"  • Hotfix branches: {self.strategy.hotfix_prefix}*")
    
    def branch_exists(self, branch_name: str) -> bool:
        """
        Check if a branch exists.
        
        Args:
            branch_name: The name of the branch to check
            
        Returns:
            True if the branch exists, False otherwise
        """
        result = subprocess.run(
            ["git", "rev-parse", "--verify", branch_name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def branch_has_upstream(self, branch_name: str) -> bool:
        """
        Check if a branch has an upstream tracking branch.
        
        Args:
            branch_name: The name of the branch to check
            
        Returns:
            True if the branch has an upstream, False otherwise
        """
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", f"{branch_name}@{{upstream}}"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def create_feature_branch(self, feature_name: str) -> str:
        """
        Create a new feature branch from the development branch.
        
        Args:
            feature_name: The name of the feature (without prefix)
            
        Returns:
            The full command that was executed
        """
        branch_name = f"{self.strategy.feature_prefix}{feature_name}"
        
        # Check if branch already exists
        if self.branch_exists(branch_name):
            print(f"  ℹ️ Branch '{branch_name}' already exists. Switching to it instead of creating.")
            command = f"git checkout {branch_name}"
            self._execute_git_command(command)
            return command
        
        # Check if we should pull (only if branch has upstream tracking)
        pull_cmd = ""
        if self.branch_exists(self.strategy.development_branch):
            if self.branch_has_upstream(self.strategy.development_branch):
                pull_cmd = " && git pull"
            else:
                print(f"  ℹ️ Development branch '{self.strategy.development_branch}' has no upstream. Skipping pull.")
        
        command = f"git checkout {self.strategy.development_branch}{pull_cmd} && git checkout -b {branch_name}"
        self._execute_git_command(command)
        return command
    
    def create_bugfix_branch(self, bug_name: str) -> str:
        """
        Create a new bugfix branch from the main branch.
        
        Args:
            bug_name: The name of the bugfix (without prefix)
            
        Returns:
            The full command that was executed
        """
        branch_name = f"{self.strategy.bugfix_prefix}{bug_name}"
        
        # Check if branch already exists
        if self.branch_exists(branch_name):
            print(f"  ℹ️ Branch '{branch_name}' already exists. Switching to it instead of creating.")
            command = f"git checkout {branch_name}"
            self._execute_git_command(command)
            return command
        
        # Check if we should pull (only if branch has upstream tracking)
        pull_cmd = ""
        if self.branch_exists(self.strategy.main_branch):
            if self.branch_has_upstream(self.strategy.main_branch):
                pull_cmd = " && git pull"
            else:
                print(f"  ℹ️ Main branch '{self.strategy.main_branch}' has no upstream. Skipping pull.")
        
        command = f"git checkout {self.strategy.main_branch}{pull_cmd} && git checkout -b {branch_name}"
        self._execute_git_command(command)
        return command
    
    def create_hotfix_branch(self, hotfix_name: str) -> str:
        """
        Create a new hotfix branch from the main branch.
        
        Args:
            hotfix_name: The name of the hotfix (without prefix)
            
        Returns:
            The full command that was executed
        """
        branch_name = f"{self.strategy.hotfix_prefix}{hotfix_name}"
        
        # Check if branch already exists
        if self.branch_exists(branch_name):
            print(f"  ℹ️ Branch '{branch_name}' already exists. Switching to it instead of creating.")
            command = f"git checkout {branch_name}"
            self._execute_git_command(command)
            return command
        
        # Check if we should pull (only if branch has upstream tracking)
        pull_cmd = ""
        if self.branch_exists(self.strategy.main_branch):
            if self.branch_has_upstream(self.strategy.main_branch):
                pull_cmd = " && git pull"
            else:
                print(f"  ℹ️ Main branch '{self.strategy.main_branch}' has no upstream. Skipping pull.")
        
        command = f"git checkout {self.strategy.main_branch}{pull_cmd} && git checkout -b {branch_name}"
        self._execute_git_command(command)
        return command
    
    def merge_feature_to_dev(self, feature_name: str) -> None:
        """
        Merge a feature branch back to the development branch.
        
        Args:
            feature_name: The name of the feature (without prefix)
        """
        branch_name = f"{self.strategy.feature_prefix}{feature_name}"
        
        # Check if we should pull (only if branch has upstream tracking)
        pull_cmd = ""
        if self.branch_exists(self.strategy.development_branch):
            if self.branch_has_upstream(self.strategy.development_branch):
                pull_cmd = " && git pull"
            else:
                print(f"  ℹ️ Development branch '{self.strategy.development_branch}' has no upstream. Skipping pull.")
        
        self._execute_git_command(f"git checkout {self.strategy.development_branch}{pull_cmd}")
        self._execute_git_command(f"git merge --no-ff {branch_name}")
    
    def list_branches(self, prefix: Optional[str] = None) -> List[str]:
        """
        List all branches matching the given prefix.
        
        Best practice:
        - Regularly review branches to identify stale or abandoned branches
        - Clean up merged branches to keep repository tidy
        - Use branch prefixes to organize and categorize work
        
        Args:
            prefix: Branch prefix to filter by (e.g., 'feature/', 'bugfix/')
            
        Returns:
            List of branch names matching the prefix
        """
        print(f"\n📋 Listing{'':s} branches{f' with prefix {prefix}' if prefix else ''}")
        
        result = subprocess.run(
            ["git", "branch", "--list"], 
            capture_output=True, 
            text=True,
            check=True
        )
        
        branches = [
            branch.strip().lstrip("* ") 
            for branch in result.stdout.splitlines() 
            if branch.strip()
        ]
        
        if prefix:
            branches = [branch for branch in branches if branch.startswith(prefix)]
            
        if branches:
            print(f"  ✅ Found {len(branches)} matching branches:")
            current_branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            for branch in branches:
                is_current = branch == current_branch
                print(f"  {'*' if is_current else ' '} {branch}")
        else:
            print(f"  ℹ️ No{f' {prefix}' if prefix else ''} branches found")
            
        return branches
    
    def _execute_git_command(self, command: str) -> subprocess.CompletedProcess:
        """
        Execute a git command.
        
        Best practice:
        - Capture command output for debugging
        - Handle errors gracefully with informative messages
        - Use shell=True for complex commands with &&
        
        Args:
            command: Git command to execute
            
        Returns:
            Completed process object
        """
        try:
            return subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Git command failed: {e}")
            print(f"  ℹ️ Command was: {command}")
            raise


if __name__ == "__main__":
    # Example usage with narrative output
    print("=" * 80)
    print("🌿 GIT BRANCHING STRATEGY DEMONSTRATION")
    print("=" * 80)
    print("\nThis script showcases recommended Git branching strategies and workflows")
    print("that help maintain a clean repository and facilitate collaborative development.")
    
    git = GitBranching()
    
    print("\n📚 BRANCHING STRATEGY OVERVIEW:")
    print(f"  • Main branch ({git.strategy.main_branch}): Production-ready code")
    print(f"  • Development branch ({git.strategy.development_branch}): Code for next release")
    print(f"  • Feature branches ({git.strategy.feature_prefix}*): New functionality")
    print(f"  • Bugfix branches ({git.strategy.bugfix_prefix}*): Production issue fixes")
    print(f"  • Hotfix branches ({git.strategy.hotfix_prefix}*): Critical production fixes")
    
    print("\n🔄 TYPICAL WORKFLOWS:")
    
    print("\n1. FEATURE DEVELOPMENT")
    print("   ↓ Start from development branch")
    print(f"   ↓ Create feature branch: {git.strategy.feature_prefix}new-feature")
    print("   ↓ Make changes and commit")
    print(f"   ↓ Merge back to {git.strategy.development_branch} with --no-ff")
    
    print("\n2. BUGFIX WORKFLOW")
    print("   ↓ Start from main branch")
    print(f"   ↓ Create bugfix branch: {git.strategy.bugfix_prefix}fix-issue")
    print("   ↓ Fix bug and commit")
    print(f"   ↓ Merge to {git.strategy.main_branch}")
    print(f"   ↓ Merge to {git.strategy.development_branch}")
    
    print("\n3. HOTFIX WORKFLOW")
    print("   ↓ Start from main branch")
    print(f"   ↓ Create hotfix branch: {git.strategy.hotfix_prefix}critical-fix")
    print("   ↓ Fix critical issue and commit")
    print(f"   ↓ Merge to {git.strategy.main_branch} with version bump")
    print("   ↓ Deploy to production")
    print(f"   ↓ Merge to {git.strategy.development_branch}")
    
    # Demonstrate creating a feature branch
    print("\n🔍 DEMONSTRATION: Creating a feature branch")
    print("-" * 50)
    command = git.create_feature_branch("user-authentication")
    
    # List feature branches
    print("\n🔍 DEMONSTRATION: Listing feature branches")
    print("-" * 50)
    git.list_branches(git.strategy.feature_prefix)
    
    print("\n" + "=" * 80)
    print("For more information on Git branching strategies, visit:")
    print("https://nvie.com/posts/a-successful-git-branching-model/")
    print("=" * 80)