print("Testing Python environment...")
print("If you can see this, Python is working!")

# Test Flask import
try:
    import flask
    print("✅ Flask is installed")
    print(f"Flask version: {flask.__version__}")
except ImportError:
    print("❌ Flask is not installed")
