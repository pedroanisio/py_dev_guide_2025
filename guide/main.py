#!/usr/bin/env python3
"""
Python Best Practices - Integrated Demo Application

This module serves as the main entry point for demonstrating how all
the individual best practice modules work together to form a complete
application. It orchestrates the various components while preserving
their educational value.
"""

import logging
import os
import sys
import argparse
from pathlib import Path

# Import our best practice modules
from dry import DRY
from solid import SOLID
from environment import EnvironmentManagement
from observability import LoggingObservabilityStandards
from modern import ModernPythonSyntax
from validation import DataValidationAndConfiguration
from tasks import BackgroundTasksAndConcurrency
from fast_api_best_practice import FastAPIBestPractices
from git_branching import GitBranching


class IntegratedDemoApplication:
    """
    Demonstrates how all best practice modules work together
    in a cohesive application architecture.
    """
    
    def __init__(self):
        """Initialize the integrated demo application."""
        self.app_name = "PyBestPractices"
        
        # Setup structured logging first (foundation for all other components)
        self.logging_standards = LoggingObservabilityStandards()
        self.logger = self.logging_standards.create_basic_jsonl_logger()
        self.logger.info("Initializing integrated demo application", app_name=self.app_name)
        
        # Initialize environment
        self.env_manager = EnvironmentManagement()
        self.logger.info("Environment manager initialized", branching_strategy=str(self.env_manager.branching_strategy))
        
        # Initialize git branching utilities
        self.git_manager = GitBranching()
        
        # Initialize data validation system
        self.validation_system = DataValidationAndConfiguration()
        
        # Initialize background task system
        self.task_system = BackgroundTasksAndConcurrency()
        
        # Core principles (educational components)
        self.dry_principle = DRY()
        self.solid_principles = SOLID()
        self.modern_syntax = ModernPythonSyntax()
        
        # The API application (primary interface)
        self.api = FastAPIBestPractices()
        
        self.logger.info("All components initialized successfully")
    
    def run_standalone_demo(self):
        """Run a demonstration that shows all components working together."""
        print("\n" + "=" * 80)
        print(f"🚀 {self.app_name} - INTEGRATED BEST PRACTICES DEMO")
        print("=" * 80)
        
        # Show core principles in action
        print("\n📚 Core Programming Principles:")
        print(f"• {self.dry_principle}")
        print(f"• {self.solid_principles}")
        
        # Demonstrate environment setup
        print("\n🛠️ Project Environment:")
        project_name = "example_project"
        print(f"• Creating pyproject.toml for {project_name}")
        pyproject_content = self.env_manager.setup_pyproject_toml(project_name)
        print(f"• Setting up virtual environment: {self.env_manager.setup_venv_command()}")
        
        # Demonstrate git workflow
        print("\n📋 Git Workflow:")
        feature_name = "user-authentication"
        feature_branch_cmd = self.git_manager.create_feature_branch(feature_name)
        print(f"• Feature branch command: {feature_branch_cmd}")
        
        # Demonstrate data validation
        print("\n✅ Data Validation:")
        settings_example = self.validation_system.generate_settings_example()
        print(f"• Generated settings class with validation")
        
        # Demonstrate background tasks
        print("\n🔄 Background Tasks:")
        celery_config = self.task_system.get_celery_task_decorator("critical")
        print(f"• Critical task configuration prepared")
        
        # Start the API (last step)
        print("\n🌐 API Service:")
        print("• Starting FastAPI application (press Ctrl+C to exit)")
        
        # Run the actual API server
        self.api.run_demo()
    
    def parse_args(self):
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description="Python Best Practices Integrated Demo")
        parser.add_argument("--component", type=str, choices=[
            "all", "api", "tasks", "logging", "validation", "environment", 
            "git", "solid", "dry", "modern"
        ], default="all", help="Specific component to demonstrate")
        
        return parser.parse_args()
    
    def run(self):
        """Run the demo based on command line arguments."""
        args = self.parse_args()
        
        if args.component == "all":
            self.run_standalone_demo()
        elif args.component == "api":
            self.api.run_demo()
        elif args.component == "tasks":
            print(f"📋 {self.task_system.name} Demo:")
            print(self.task_system.get_celery_example())
        elif args.component == "logging":
            print(f"📋 {self.logging_standards.name} Demo:")
            print(self.logging_standards.get_structlog_implementation())
        elif args.component == "validation":
            print(f"📋 {self.validation_system.name} Demo:")
            for principle in self.validation_system.core_principles:
                print(f"\n• {principle.name}: {principle.description}")
        elif args.component == "environment":
            print(f"📋 {self.env_manager.name} Demo:")
            print(self.env_manager.setup_pyproject_toml("demo_project"))
        elif args.component == "git":
            print(f"📋 Git Branching Strategy Demo:")
            print(self.git_manager.create_feature_branch("example-feature"))
        elif args.component == "solid":
            print(f"📋 SOLID Principles Demo:")
            for letter in "SOLID":
                principle = self.solid_principles.get_principle(letter)
                print(f"\n• {principle['name']} Principle: {principle['description']}")
        elif args.component == "dry":
            print(f"📋 {self.dry_principle} Demo:")
            examples = self.dry_principle.get_examples()
            print("\nNon-DRY Code Example:")
            print(examples["non_dry"])
            print("\nDRY Code Example:")
            print(examples["dry"])
        elif args.component == "modern":
            print(f"📋 {self.modern_syntax.name} Demo:")
            print(f"Recommended Python Version: {self.modern_syntax.preferred_version}")


if __name__ == "__main__":
    app = IntegratedDemoApplication()
    app.run() 