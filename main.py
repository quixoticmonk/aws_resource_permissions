import requests
import json
import sys
from typing import Optional, List, Dict

class CloudFormationPermissionsExtractor:
    def __init__(self):
        self.base_url = "https://cloudformation-schema.s3.us-west-2.amazonaws.com/resourcetype"
        self.valid_operations = {'create', 'read', 'update', 'delete', 'list'}

    def format_resource_type(self, resource_type: str) -> str:
        """Convert CloudFormation resource type to schema format."""
        return resource_type.replace('::', '-')

    def get_schema(self, resource_type: str) -> Dict:
        """Fetch the schema for the given resource type."""
        formatted_type = self.format_resource_type(resource_type)
        try:
            response = requests.get(f"{self.base_url}/{formatted_type}.json")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching schema: {e}")
            sys.exit(1)

    def extract_permissions(self, schema: Dict, operation: Optional[str] = None) -> Dict[str, List[str]]:
        """Extract permissions from the schema for specified operation."""
        handlers = schema.get('handlers', {})
        permissions = {}

        # If no specific operation is requested, get permissions for all operations
        operations_to_check = [operation.lower()] if operation else self.valid_operations

        for op in operations_to_check:
            if op in handlers:
                permissions[op] = handlers[op].get('permissions', [])

        return permissions

    def display_permissions(self, permissions: Dict[str, List[str]]):
        """Display the extracted permissions in a formatted way."""
        if not permissions:
            print("No permissions found for the specified criteria.")
            return

        print("\nRequired Permissions:")
        print("-" * 50)
        for operation, perms in permissions.items():
            print(f"\n{operation.upper()} permissions:")
            if perms:
                for perm in perms:
                    print(f"  - {perm}")
            else:
                print("  No specific permissions defined")

def main():
    extractor = CloudFormationPermissionsExtractor()

    # Get resource type from user
    resource_type = input("Enter CloudFormation resource type (e.g., AWS::S3::Bucket): ").strip()
    if not resource_type:
        print("Resource type is required.")
        return

    # Get optional operation type
    print("\nAvailable operations: create, read, update, delete, list")
    print("Press Enter to see all permissions")
    operation = input("Enter operation type (optional): ").strip().lower()

    # Validate operation if provided
    if operation and operation not in extractor.valid_operations:
        print(f"Invalid operation. Valid operations are: {', '.join(extractor.valid_operations)}")
        return

    # Get and process schema
    schema = extractor.get_schema(resource_type)
    permissions = extractor.extract_permissions(schema, operation)
    extractor.display_permissions(permissions)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
