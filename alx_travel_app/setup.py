#!/usr/bin/env python3
"""
Setup script for ALX Travel App with Chapa API Integration
This script helps set up the project and run initial tests
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("   Please use Python 3.8 or higher")
        return False


def create_virtual_environment():
    """Create a virtual environment"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("🔄 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def install_dependencies():
    """Install Python dependencies"""
    if not Path("venv").exists():
        print("❌ Virtual environment not found. Please create it first.")
        return False
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_path = "venv/bin/pip"
    
    if not Path(pip_path).exists():
        print(f"❌ Pip not found at {pip_path}")
        return False
    
    return run_command(f"{pip_path} install -r requirements.txt", "Installing dependencies")


def setup_environment():
    """Set up environment variables"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ Environment file already exists")
        return True
    
    if not env_example.exists():
        print("❌ Environment template not found")
        return False
    
    print("🔄 Creating environment file...")
    try:
        shutil.copy(env_example, env_file)
        print("✅ Environment file created from template")
        print("⚠️  Please edit .env file with your actual values:")
        print("   - CHAPA_SECRET_KEY")
        print("   - EMAIL_HOST_USER")
        print("   - EMAIL_HOST_PASSWORD")
        return True
    except Exception as e:
        print(f"❌ Failed to create environment file: {e}")
        return False


def run_django_commands():
    """Run Django setup commands"""
    if not Path("venv").exists():
        print("❌ Virtual environment not found. Please create it first.")
        return False
    
    # Determine the correct python path
    if os.name == 'nt':  # Windows
        python_path = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_path = "venv/bin/python"
    
    if not Path(python_path).exists():
        print(f"❌ Python not found at {python_path}")
        return False
    
    commands = [
        (f"{python_path} manage.py makemigrations", "Creating database migrations"),
        (f"{python_path} manage.py migrate", "Running database migrations"),
        (f"{python_path} manage.py collectstatic --noinput", "Collecting static files"),
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
    
    return success


def create_superuser():
    """Create a superuser account"""
    if not Path("venv").exists():
        print("❌ Virtual environment not found. Please create it first.")
        return False
    
    # Determine the correct python path
    if os.name == 'nt':  # Windows
        python_path = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_path = "venv/bin/python"
    
    if not Path(python_path).exists():
        print(f"❌ Python not found at {python_path}")
        return False
    
    print("\n👤 Creating superuser account...")
    print("   Please follow the prompts to create your admin account")
    
    try:
        subprocess.run([python_path, "manage.py", "createsuperuser"], check=True)
        print("✅ Superuser created successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Superuser creation was cancelled or failed")
        return False


def test_chapa_integration():
    """Test the Chapa API integration"""
    if not Path("venv").exists():
        print("❌ Virtual environment not found. Please create it first.")
        return False
    
    # Determine the correct python path
    if os.name == 'nt':  # Windows
        python_path = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_path = "venv/bin/python"
    
    if not Path(python_path).exists():
        print(f"❌ Python not found at {python_path}")
        return False
    
    print("\n🧪 Testing Chapa API integration...")
    return run_command(
        f"{python_path} manage.py test_chapa --create-data",
        "Running Chapa integration tests"
    )


def main():
    """Main setup function"""
    print("🚀 ALX Travel App Setup with Chapa API Integration")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Setup failed at virtual environment creation")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Setup failed at environment setup")
        sys.exit(1)
    
    # Run Django commands
    if not run_django_commands():
        print("❌ Setup failed at Django setup")
        sys.exit(1)
    
    # Create superuser
    create_superuser()
    
    # Test Chapa integration
    test_chapa_integration()
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your actual values")
    print("2. Start the development server:")
    print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("   python manage.py runserver")
    print("3. Visit http://localhost:8000/admin to access the admin panel")
    print("4. Test the Chapa API integration with sandbox credentials")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
