import asyncio
import os
import django
from dotenv import load_dotenv
# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

load_dotenv()  # Load environment variables from .env file
from agents.allisson import AllissonAgent

async def test_allisson():
    """Test Allisson routing and Hannah execution"""
    
    print("=" * 60)
    print("🧪 TESTING ALLISSON EMPIRE")
    print("=" * 60)
    print()
    
    # Create Allisson
    allisson = AllissonAgent()
    
    # Test 1: Simple greeting
    print("Test 1: Simple greeting")
    print("-" * 60)
    result = await allisson.execute("Hello Allisson!")
    print(f"Result: {result}")
    print()
    
    # Test 2: Social media post (should route to Hannah)
    print("Test 2: Post a tweet")
    print("-" * 60)
    result = await allisson.execute("Post a tweet about AI transforming the world")
    print(f"Result: {result}")
    print()
    
    # Test 3: System status
    print("Test 3: System status")
    print("-" * 60)
    result = await allisson.execute("What's the system status?")
    print(f"Result: {result}")
    print()
    
    print("=" * 60)
    print("✅ ALL TESTS COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_allisson())