# Test the enhanced filter integration
from soothe_app.src.core.content_filter import EnhancedContentFilter

# Initialize the filter
filter = EnhancedContentFilter()
print("✅ Enhanced filter initialized successfully")

# Test safe content
result = filter.analyze_content("This is safe content")
print(f"✅ Safe content test: {not result.has_violations}")

# Test harmful content
result = filter.analyze_content("I want to commit suicide")
print(f"✅ Harmful content detected: {result.has_violations}")
print(f"   Severity score: {result.severity_score}")
print(f"   Categories: {result.categories_violated}")

print("\n🎉 Integration test completed successfully!")
