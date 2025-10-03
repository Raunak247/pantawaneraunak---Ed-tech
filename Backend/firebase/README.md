# Firebase Module

Firebase integration module for the Adaptive Learning Backend.

## Components

- `__init__.py`: Firebase configuration and initialization
- `firestore_helpers.py`: Helper functions for Firestore operations
- `upload_data.py`: Utility to upload data to Firestore
- `credentials/`: Store Firebase credentials (not tracked in Git)

## Usage

```python
# To use Firestore in your application
from firebase.firestore_helpers import get_collection

# Example: Get all users
users = get_collection('users').stream()
```

For detailed setup and usage, see the [Firebase Setup Guide](../docs/firebase/README.md).