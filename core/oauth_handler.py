"""
OAuth/SSO Handler for Chainlit Applications
Reusable authentication module for Microsoft Entra ID (Azure AD)
"""
import os
import logging
from typing import Optional, Callable, Dict, Any, Tuple, List
import chainlit as cl

logger = logging.getLogger(__name__)


class OAuthHandler:
    """
    Reusable OAuth/SSO handler for Chainlit applications.
    Supports Microsoft Entra ID (Azure AD) authentication.
    
    Usage:
        oauth_handler = OAuthHandler()
        
        @cl.oauth_callback
        async def oauth_callback(provider_id, token, raw_user_data, default_user, id_token=None):
            return await oauth_handler.handle_callback(
                provider_id, token, raw_user_data, default_user, id_token
            )
    """
    
    def __init__(
        self,
        allowed_providers: Optional[List[str]] = None,
        user_metadata_extractor: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    ):
        """
        Initialize OAuth handler.
        
        Args:
            allowed_providers: List of OAuth provider IDs to accept.
                             Default: ["azure-ad", "azure-ad-hybrid"]
            user_metadata_extractor: Custom function to extract user metadata from raw_user_data.
                                   Default: Extracts Azure AD standard fields
        """
        self.allowed_providers = allowed_providers or ["azure-ad", "azure-ad-hybrid"]
        self.user_metadata_extractor = user_metadata_extractor or self._default_metadata_extractor
    
    def _default_metadata_extractor(self, raw_user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default metadata extraction from Azure AD user profile.
        
        Args:
            raw_user_data: User profile data from Microsoft Graph API
        
        Returns:
            Dictionary with extracted user metadata
        """
        email = raw_user_data.get("mail") or raw_user_data.get("userPrincipalName")
        display_name = raw_user_data.get("displayName", "Unknown User")
        
        return {
            "name": display_name,
            "email": email,
            "job_title": raw_user_data.get("jobTitle", ""),
            "department": raw_user_data.get("department", ""),
            "raw_user_data": raw_user_data
        }
    
    async def handle_callback(
        self,
        provider_id: str,
        token: str,
        raw_user_data: Dict[str, Any],
        default_user: cl.User,
        id_token: Optional[str] = None
    ) -> Optional[cl.User]:
        """
        OAuth callback handler for authentication.
        
        This function should be registered via @cl.oauth_callback decorator.
        It receives the access token and user profile from the OAuth provider.
        
        Args:
            provider_id: OAuth provider identifier (e.g., "azure-ad")
            token: OAuth access token from the provider
            raw_user_data: User profile data from the provider's API
            default_user: Chainlit's default user object (can be customized)
            id_token: Optional ID token (for hybrid flow)
        
        Returns:
            cl.User object with persistent identifier, or None if authentication fails
        """
        try:
            # Check if this is an allowed provider
            if provider_id not in self.allowed_providers:
                logger.warning(f"Unknown or unauthorized provider: {provider_id}")
                return None
            
            # Extract user information using the configured extractor
            metadata = self.user_metadata_extractor(raw_user_data)
            email = metadata.get("email")
            display_name = metadata.get("name", "Unknown User")
            
            if not email:
                logger.error("No email found in user data - cannot authenticate")
                logger.error(f"Raw user data: {raw_user_data}")
                return None
            
            logger.info(f"✅ OAuth success: {email} ({display_name})")
            
            # Create Chainlit User object
            # The 'identifier' field is used as the persistent user_id across sessions
            user = cl.User(
                identifier=email,  # This becomes the user_id in data storage
                metadata={
                    **metadata,
                    "provider": provider_id,
                    "token": token  # Store for API calls if needed
                }
            )
            
            return user
            
        except Exception as e:
            logger.error(f"❌ OAuth callback failed: {e}", exc_info=True)
            return None
    
    @staticmethod
    def validate_env_vars(
        required_vars: Optional[List[str]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate that required OAuth environment variables are set.
        
        Args:
            required_vars: List of environment variable names to check.
                         Default: Azure AD OAuth variables
        
        Returns:
            Tuple of (is_valid, missing_vars)
            - is_valid: True if all variables are set
            - missing_vars: List of missing variable names
        """
        if required_vars is None:
            required_vars = [
                "OAUTH_AZURE_AD_CLIENT_ID",
                "OAUTH_AZURE_AD_CLIENT_SECRET",
                "OAUTH_AZURE_AD_TENANT_ID"
            ]
        
        env_values = {var: os.getenv(var) for var in required_vars}
        missing = [k for k, v in env_values.items() if not v]
        
        return (len(missing) == 0, missing)
    
    @staticmethod
    def log_oauth_status(
        required_vars: Optional[List[str]] = None,
        verbose: bool = True
    ):
        """
        Log OAuth configuration status to console.
        
        Args:
            required_vars: List of environment variable names to check.
                         Default: Azure AD OAuth variables
            verbose: If True, show status of each variable
        """
        if required_vars is None:
            required_vars = [
                "OAUTH_AZURE_AD_CLIENT_ID",
                "OAUTH_AZURE_AD_CLIENT_SECRET",
                "OAUTH_AZURE_AD_TENANT_ID"
            ]
        
        is_valid, missing = OAuthHandler.validate_env_vars(required_vars)
        
        if missing:
            print(f"⚠️  WARNING: Missing OAuth environment variables: {', '.join(missing)}")
            print(f"⚠️  OAuth/SSO will not be available. Please check your .env file.")
        else:
            print(f"✅ OAuth configuration loaded successfully")
            
            if verbose:
                for var in required_vars:
                    value = os.getenv(var)
                    status = "✓ Set" if value else "✗ Missing"
                    print(f"   {var}: {status}")
    
    @staticmethod
    def ensure_env_vars_loaded():
        """
        Force reload of OAuth environment variables.
        
        This ensures OAuth config is available even if loaded after dotenv.
        Call this at module initialization if needed.
        """
        oauth_vars = [
            "OAUTH_AZURE_AD_CLIENT_ID",
            "OAUTH_AZURE_AD_CLIENT_SECRET",
            "OAUTH_AZURE_AD_TENANT_ID"
        ]
        
        for var in oauth_vars:
            value = os.getenv(var, "")
            os.environ.setdefault(var, value)


def create_oauth_callback(handler: Optional[OAuthHandler] = None) -> Callable:
    """
    Factory function to create a Chainlit OAuth callback decorator.
    
    Args:
        handler: OAuthHandler instance. If None, creates a default handler.
    
    Returns:
        Async function suitable for @cl.oauth_callback decorator
    
    Usage:
        # Option 1: Use default handler
        oauth_callback = create_oauth_callback()
        
        # Option 2: Use custom handler
        handler = OAuthHandler(allowed_providers=["azure-ad"])
        oauth_callback = create_oauth_callback(handler)
    """
    if handler is None:
        handler = OAuthHandler()
    
    async def oauth_callback(
        provider_id: str,
        token: str,
        raw_user_data: Dict[str, Any],
        default_user: cl.User,
        id_token: Optional[str] = None
    ) -> Optional[cl.User]:
        return await handler.handle_callback(
            provider_id, token, raw_user_data, default_user, id_token
        )
    
    return oauth_callback
