"""
Cleanup Reporter Module

This module provides reporting functionality for cleanup operations, including
summary reports, skipped resource reports, and identification method reports.

Requirements: 4.1, 4.2, 4.4, 4.5
"""

import sys
import os

# Add repository root to path for i18n imports
# Navigate 3 levels up from iot_helpers/cleanup/reporter.py to repository root
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from i18n.loader import load_messages


class CleanupReporter:
    """
    Reporter for cleanup operations.
    
    Provides methods for displaying cleanup summaries, skipped resources,
    and identification methods used during cleanup.
    """
    
    def __init__(self, language='en'):
        """
        Initialize the cleanup reporter.
        
        Args:
            language: Language code for i18n messages (default: 'en')
        """
        self.messages = load_messages('cleanup_reporter', language)
    
    def get_message(self, key, *args):
        """
        Get a localized message.
        
        Args:
            key: Message key in dot notation (e.g., 'summary.header')
            *args: Arguments to format into the message
            
        Returns:
            Formatted message string
        """
        # Navigate through nested dictionary using dot notation
        keys = key.split('.')
        value = self.messages
        for k in keys:
            value = value.get(k, {})
        
        # Format with arguments if provided
        if args and isinstance(value, str):
            return value.format(*args)
        return value if isinstance(value, str) else key

    def report_summary(self, stats, dry_run=False, execution_time=None):
        """
        Display a summary of cleanup operations.
        
        Args:
            stats: Dictionary of statistics by resource type
                   Format: {
                       'resource_type': {
                           'total': int,
                           'deleted': int,
                           'skipped': int,
                           'failed': int
                       }
                   }
            dry_run: Whether this was a dry-run operation
            execution_time: Optional execution time in seconds
            
        Requirements: 4.1, 4.2, 6.4
        """
        # Calculate totals across all resource types
        total_deleted = sum(s.get('deleted', 0) for s in stats.values())
        total_skipped = sum(s.get('skipped', 0) for s in stats.values())
        total_failed = sum(s.get('failed', 0) for s in stats.values())
        total_processed = sum(s.get('total', 0) for s in stats.values())
        
        # Display header
        print("\n" + "=" * 70)
        if dry_run:
            print(self.get_message('summary.header_dry_run'))
        else:
            print(self.get_message('summary.header'))
        print("=" * 70)
        
        # Display deleted resources section
        if total_deleted > 0 or dry_run:
            print("\n" + self.get_message('summary.deleted_section'))
            print("-" * 70)
            for resource_type, resource_stats in sorted(stats.items()):
                deleted_count = resource_stats.get('deleted', 0)
                if deleted_count > 0:
                    # Format resource type name for display
                    display_name = self._format_resource_type(resource_type)
                    print(f"  {display_name:.<50} {deleted_count:>5}")
            print("-" * 70)
            print(f"  {self.get_message('summary.total'):.<50} {total_deleted:>5}")
        
        # Display skipped resources section
        if total_skipped > 0:
            print("\n" + self.get_message('summary.skipped_section'))
            print("-" * 70)
            for resource_type, resource_stats in sorted(stats.items()):
                skipped_count = resource_stats.get('skipped', 0)
                if skipped_count > 0:
                    display_name = self._format_resource_type(resource_type)
                    reason = self.get_message('summary.non_workshop_reason')
                    print(f"  {display_name:.<40} {skipped_count:>5} ({reason})")
            print("-" * 70)
            print(f"  {self.get_message('summary.total'):.<40} {total_skipped:>5}")
        
        # Display failed resources section
        if total_failed > 0:
            print("\n" + self.get_message('summary.failed_section'))
            print("-" * 70)
            for resource_type, resource_stats in sorted(stats.items()):
                failed_count = resource_stats.get('failed', 0)
                if failed_count > 0:
                    display_name = self._format_resource_type(resource_type)
                    print(f"  {display_name:.<50} {failed_count:>5}")
            print("-" * 70)
            print(f"  {self.get_message('summary.total'):.<50} {total_failed:>5}")
        
        # Display overall summary
        print("\n" + self.get_message('summary.overall_section'))
        print("-" * 70)
        print(f"  {self.get_message('summary.total_resources_processed'):.<50} {total_processed:>5}")
        if dry_run:
            print(f"  {self.get_message('summary.would_delete'):.<50} {total_deleted:>5}")
        else:
            print(f"  {self.get_message('summary.successfully_deleted'):.<50} {total_deleted:>5}")
        print(f"  {self.get_message('summary.skipped_non_workshop'):.<50} {total_skipped:>5}")
        if total_failed > 0:
            print(f"  {self.get_message('summary.failed'):.<50} {total_failed:>5}")
        
        # Display execution time if available
        if execution_time is not None:
            print(f"  {self.get_message('summary.execution_time'):.<50} {execution_time:>5.1f}s")
        
        print("=" * 70 + "\n")
    
    def _format_resource_type(self, resource_type):
        """
        Format resource type name for display.
        
        Args:
            resource_type: Resource type identifier
            
        Returns:
            Formatted display name
        """
        # Convert underscores to spaces and title case
        return resource_type.replace('_', ' ').title()

    def report_skipped(self, resources, resource_type, debug_mode=False):
        """
        Report skipped resources.
        
        In normal mode, only shows count.
        In debug mode, shows individual resource names.
        
        Args:
            resources: List of skipped resource names
            resource_type: Type of resources
            debug_mode: Whether to show individual resource names
            
        Requirements: 4.5
        """
        if not resources:
            return
        
        count = len(resources)
        display_name = self._format_resource_type(resource_type)
        
        if debug_mode:
            # Show individual resource names in debug mode
            print(self.get_message('skipped.header_debug', display_name, count))
            for resource_name in resources:
                print(f"  - {resource_name}")
        else:
            # Only show count in normal mode
            print(self.get_message('skipped.count_only', display_name, count))

    def report_identification(self, resource_name, identification_method, is_workshop):
        """
        Report identification method used for a resource (debug mode only).
        
        Args:
            resource_name: Name of the resource
            identification_method: Method used ('tag', 'naming', 'association', 'none')
            is_workshop: Whether resource was identified as workshop resource
            
        Requirements: 4.4
        """
        # Format identification method with indicator
        if is_workshop:
            indicator = "✓"
            status = self.get_message('identification.workshop')
        else:
            indicator = "✗"
            status = self.get_message('identification.non_workshop')
        
        # Map identification method to display string
        method_display = {
            'tag': self.get_message('identification.method_tag'),
            'naming': self.get_message('identification.method_naming'),
            'association': self.get_message('identification.method_association'),
            'none': self.get_message('identification.method_none')
        }.get(identification_method, identification_method)
        
        print(f"  {indicator} {resource_name:.<50} [{method_display}] {status}")
