from urllib.parse import urlparse

def is_basic_valid_url(url):
    """Check if URL has basic validity (proper scheme and netloc) without domain restrictions."""
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and bool(parsed.netloc)

def is_valid_url(url, allowed_prefixes_or_domains):
    """Check if URL is valid based on allowed prefixes or domains."""
    parsed = urlparse(url)
    
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        return False
    
    url_lower = url.lower()
    domain = parsed.netloc.lower()
    
    # Remove port from domain if present
    if ':' in domain:
        domain = domain.split(':')[0]
    
    for allowed in allowed_prefixes_or_domains:
        allowed_lower = allowed.lower()
        
        # Check if it's a URL prefix (contains protocol or path)
        if allowed_lower.startswith(('http://', 'https://')) or '/' in allowed_lower:
            # URL prefix matching
            if url_lower.startswith(allowed_lower):
                return True
        else:
            # Domain-based matching (legacy behavior)
            if domain == allowed_lower or domain.endswith('.' + allowed_lower):
                return True
    
    return False

def filter_valid_urls(urls, allowed_prefixes_or_domains):
    """Filter URLs based on allowed prefixes or domains.
    
    If allowed_prefixes_or_domains is empty, all valid URLs are returned (no domain filtering).
    """
    if not allowed_prefixes_or_domains:
        # If no domains specified, only filter out invalid URLs (malformed, non-http/https)
        return [url for url in urls if is_basic_valid_url(url)]
    
    return [url for url in urls if is_valid_url(url, allowed_prefixes_or_domains)]

if __name__ == "__main__":
    test_urls = [
        "https://github.com/The-Pocket/PocketFlow",
        "https://github.com/The-Pocket/PocketFlow/blob/main/tests/test_async_batch_flow.py", 
        "https://github.com/The-Pocket",
        "https://github.com/other-repo",
        "https://docs.example.com/api/v1",
        "https://docs.example.com/guide",
        "https://help.example.com/faq",
        "https://example.com/blog",
        "invalid-url"
    ]
    
    print("=== Testing URL prefix matching ===")
    allowed_prefixes = ["https://github.com/The-Pocket", "https://docs.example.com/"]
    
    for url in test_urls:
        valid = is_valid_url(url, allowed_prefixes)
        print(f"{url}: {'✓' if valid else '✗'}")
    
    print(f"\nFiltered URLs: {filter_valid_urls(test_urls, allowed_prefixes)}")
    
    print("\n=== Testing domain matching ===")
    allowed_domains = ["github.com", "docs.example.com"]
    
    for url in test_urls:
        valid = is_valid_url(url, allowed_domains)
        print(f"{url}: {'✓' if valid else '✗'}")
    
    print(f"\nFiltered URLs: {filter_valid_urls(test_urls, allowed_domains)}") 