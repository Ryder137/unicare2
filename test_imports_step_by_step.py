"""
Test script to identify import issues in the UNICARE application.
Run with: python -v test_imports_step_by_step.py
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_import(module_name):
    """Test importing a module and log the result."""
    try:
        logger.info(f"Trying to import {module_name}...")
        __import__(module_name)
        logger.info(f"Successfully imported {module_name}")
        return True
    except ImportError as e:
        logger.error(f"Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error importing {module_name}: {e}")
        return False

def main():
    """Test importing all required modules."""
    # Add project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Test importing core modules
    core_modules = [
        'flask',
        'flask_login',
        'flask_sqlalchemy',
        'flask_pymongo',
        'flask_mail',
        'flask_limiter',
        'flask_wtf',
        'itsdangerous',
        'python_dotenv',
        'jwt',
        'bcrypt'
    ]
    
    # Test importing application modules
    app_modules = [
        'models.user',
        'models.admin_user',
        'models.appointment',
        'models.client',
        'routes.auth_routes',
        'routes.admin_routes',
        'routes.appointment_routes',
        'services.database_service'
    ]
    
    logger.info("Testing core module imports...")
    core_success = all(test_import(module) for module in core_modules)
    
    logger.info("\nTesting application module imports...")
    app_success = all(test_import(module) for module in app_modules)
    
    if core_success and app_success:
        logger.info("\n✅ All imports successful!")
    else:
        logger.error("\n❌ Some imports failed. Please check the logs above for details.")

if __name__ == "__main__":
    main()
