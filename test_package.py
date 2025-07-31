import src.tools.check_weather.weather_checking
from src.tools.image_crawler.ImageCrawler import AutoCrawler
import src.tools.my_calculator.calculator

def test_weather_package():
    print("Testing weather_checking package...")
    # You can add more specific tests here, e.g., calling functions from weather_checking
    # For now, just importing it is a good first step to check if it's recognized as a package.
    print(src.tools.check_weather.weather_checking.get_weather_info("London"))

def test_image_crawler_package():
    print("Testing image_crawler package...")
    try:
        crawler = AutoCrawler(
            skip_already_exist=True,
            download_path='test_downloads_image_crawler',
            full_resolution=False,
            face=False,
            no_gui=True
        )
        # Note: Actual image download requires a working internet connection and possibly a browser driver.
        # This test primarily checks if the class can be instantiated and the method called without immediate errors.
        # A full integration test would involve checking downloaded files.
        # For a quick package functionality check, we'll try a very small, non-intrusive download or just instantiate.
        
        # We'll skip actual download for automated testing to avoid external dependencies and long execution.
        # A successful instantiation and call without errors indicates the package structure is correct.
        print("ImageCrawler instantiated successfully.")
        
        print("\nAttempting to download a single image for 'The University of Melbourne'...")
        # This test requires a working internet connection and a compatible Chrome/browser driver setup.
        # If this test fails, ensure you have the necessary browser driver installed and in your PATH.
        success = crawler.download_keyword_images("The University of Melbourne", 5)
        print(f"ImageCrawler download test result for 'The University of Melbourne': {success}")
        
        print("ImageCrawler package test completed.")
    except Exception as e:
        print(f"Error testing image_crawler package: {e}")

def test_my_calculator_package():
    print("Testing my_calculator package...")
    test_cases = [
        ("10 + 5", 15),
        ("2 * 3 + 4", 10),
        ("20 / 4", 5),
        ("8 - 2 * 3", 2),
        ("2^4", 16)
    ]
    
    for expression, expected_result in test_cases:
        result = src.tools.my_calculator.calculator.calculator_tool(expression)
        if result["error"]:
            print(f"  ❌ Error for '{expression}': {result['error']}")
        elif result["result"] == expected_result:
            print(f"  ✅ '{expression}' = {result['result']} (Expected: {expected_result})")
        else:
            print(f"  ❌ '{expression}' = {result['result']} (Expected: {expected_result})")
    print("My_calculator package test completed.")

if __name__ == "__main__":
    test_weather_package()
    print("\n")
    test_image_crawler_package()
    print("\n")
    test_my_calculator_package()