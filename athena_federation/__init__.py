"""Version number of our project"""

import toml

__version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"]

# Import the SDK
from .athena_data_source import AthenaDataSource  # noqa: F401
from .lambda_handler import AthenaLambdaHandler  # noqa: F401
from .main import main  # noqa: F401
from .models import *  # noqa: F401,F403
from .sdk import AthenaFederationSDK  # noqa: F401
from .utils import AthenaSDKUtils  # noqa: F401
