"""Tests for the StackManager module."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from botocore.exceptions import ClientError
from awslabs.cfn_mcp_server.stack_manager import StackManager


class TestStackManager:
    """Test cases for StackManager."""
    
    @pytest.fixture
    def stack_manager(self):
        """Create a StackManager instance for testing."""
        with patch('awslabs.cfn_mcp_server.stack_manager.get_aws_client') as mock_client:
            manager = StackManager('us-east-1')
            manager.client = Mock()
            return manager
    
    @pytest.mark.asyncio
    async def test_deploy_new_stack(self, stack_manager):
        """Test deploying a new stack."""
        # Mock stack doesn't exist
        stack_manager.client.describe_stacks.side_effect = ClientError(
            {'Error': {'Code': 'ValidationError', 'Message': 'Stack does not exist'}},
            'DescribeStacks'
        )
        
        # Mock successful stack creation
        stack_manager.client.create_stack.return_value = {
            'StackId': 'arn:aws:cloudformation:us-east-1:123456789012:stack/test-stack/12345'
        }
        
        result = await stack_manager.deploy_stack(
            stack_name='test-stack',
            template_body='{"Resources": {}}',
            wait_for_completion=False
        )
        
        assert result['success'] is True
        assert result['operation'] == 'CREATE'
        assert result['stack_name'] == 'test-stack'
        assert 'stack_id' in result
    
    @pytest.mark.asyncio
    async def test_deploy_existing_stack(self, stack_manager):
        """Test updating an existing stack."""
        # Mock stack exists
        stack_manager.client.describe_stacks.return_value = {
            'Stacks': [{'StackName': 'test-stack', 'StackStatus': 'CREATE_COMPLETE'}]
        }
        
        # Mock successful stack update
        stack_manager.client.update_stack.return_value = {
            'StackId': 'arn:aws:cloudformation:us-east-1:123456789012:stack/test-stack/12345'
        }
        
        result = await stack_manager.deploy_stack(
            stack_name='test-stack',
            template_body='{"Resources": {}}',
            wait_for_completion=False
        )
        
        assert result['success'] is True
        assert result['operation'] == 'UPDATE'
        assert result['stack_name'] == 'test-stack'
    
    @pytest.mark.asyncio
    async def test_deploy_no_updates_needed(self, stack_manager):
        """Test deploying when no updates are needed."""
        # Mock stack exists
        stack_manager.client.describe_stacks.return_value = {
            'Stacks': [{'StackName': 'test-stack', 'StackStatus': 'CREATE_COMPLETE'}]
        }
        
        # Mock no updates needed
        stack_manager.client.update_stack.side_effect = ClientError(
            {'Error': {'Code': 'ValidationError', 'Message': 'No updates are to be performed'}},
            'UpdateStack'
        )
        
        result = await stack_manager.deploy_stack(
            stack_name='test-stack',
            template_body='{"Resources": {}}',
            wait_for_completion=False
        )
        
        assert result['success'] is True
        assert result['operation'] == 'NO_UPDATE'
    
    @pytest.mark.asyncio
    async def test_get_stack_status(self, stack_manager):
        """Test getting stack status."""
        # Mock stack information
        stack_manager.client.describe_stacks.return_value = {
            'Stacks': [{
                'StackName': 'test-stack',
                'StackStatus': 'CREATE_COMPLETE',
                'CreationTime': '2023-01-01T00:00:00Z',
                'Description': 'Test stack',
                'Parameters': [],
                'Tags': [],
                'Outputs': []
            }]
        }
        
        # Mock resources
        stack_manager.client.describe_stack_resources.return_value = {
            'StackResources': [{
                'LogicalResourceId': 'TestResource',
                'ResourceType': 'AWS::S3::Bucket',
                'ResourceStatus': 'CREATE_COMPLETE'
            }]
        }
        
        # Mock events
        stack_manager.client.describe_stack_events.return_value = {
            'StackEvents': [{
                'EventId': '12345',
                'StackName': 'test-stack',
                'LogicalResourceId': 'test-stack',
                'ResourceStatus': 'CREATE_COMPLETE',
                'Timestamp': '2023-01-01T00:00:00Z'
            }]
        }
        
        result = await stack_manager.get_stack_status(
            stack_name='test-stack',
            include_resources=True,
            include_events=True
        )
        
        assert result['success'] is True
        assert result['stack_name'] == 'test-stack'
        assert result['stack_status'] == 'CREATE_COMPLETE'
        assert 'resources' in result
        assert 'events' in result
    
    @pytest.mark.asyncio
    async def test_delete_stack(self, stack_manager):
        """Test deleting a stack."""
        stack_manager.client.delete_stack.return_value = {}
        
        result = await stack_manager.delete_stack(
            stack_name='test-stack',
            wait_for_completion=False
        )
        
        assert result['success'] is True
        assert result['operation'] == 'DELETE'
        assert result['stack_name'] == 'test-stack'
    
    @pytest.mark.asyncio
    async def test_stack_exists_true(self, stack_manager):
        """Test checking if stack exists (true case)."""
        stack_manager.client.describe_stacks.return_value = {
            'Stacks': [{'StackName': 'test-stack'}]
        }
        
        exists = await stack_manager._stack_exists('test-stack')
        assert exists is True
    
    @pytest.mark.asyncio
    async def test_stack_exists_false(self, stack_manager):
        """Test checking if stack exists (false case)."""
        stack_manager.client.describe_stacks.side_effect = ClientError(
            {'Error': {'Code': 'ValidationError', 'Message': 'Stack does not exist'}},
            'DescribeStacks'
        )
        
        exists = await stack_manager._stack_exists('test-stack')
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_deploy_with_parameters_and_tags(self, stack_manager):
        """Test deploying with parameters and tags."""
        # Mock stack doesn't exist
        stack_manager.client.describe_stacks.side_effect = ClientError(
            {'Error': {'Code': 'ValidationError', 'Message': 'Stack does not exist'}},
            'DescribeStacks'
        )
        
        stack_manager.client.create_stack.return_value = {
            'StackId': 'arn:aws:cloudformation:us-east-1:123456789012:stack/test-stack/12345'
        }
        
        parameters = [{'ParameterKey': 'Environment', 'ParameterValue': 'test'}]
        tags = [{'Key': 'Project', 'Value': 'TestProject'}]
        capabilities = ['CAPABILITY_IAM']
        
        result = await stack_manager.deploy_stack(
            stack_name='test-stack',
            template_body='{"Resources": {}}',
            parameters=parameters,
            tags=tags,
            capabilities=capabilities,
            wait_for_completion=False
        )
        
        assert result['success'] is True
        
        # Verify the client was called with correct parameters
        stack_manager.client.create_stack.assert_called_once()
        call_args = stack_manager.client.create_stack.call_args[1]
        assert call_args['Parameters'] == parameters
        assert call_args['Tags'] == tags
        assert call_args['Capabilities'] == capabilities
