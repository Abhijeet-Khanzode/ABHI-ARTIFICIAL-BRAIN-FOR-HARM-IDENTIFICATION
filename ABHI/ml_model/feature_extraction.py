from urllib.parse import urlparse
import re
import os


def load_safe_domains(filepath="ABHI/CSV/known_safe_domains.txt"):
    try:
        # Make the filepath absolute relative to this script
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        abs_path = os.path.join(base_dir, filepath)
        
        with open(abs_path, "r") as f:
            return set(domain.strip().lower() for domain in f if domain.strip())
    
    except Exception as e:
        print(f"❌ Error loading safe domains: {e}")
        return set()


# 📂 Load once at top
KNOWN_SAFE_DOMAINS = load_safe_domains()

def extract_features(url):
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path = parsed.path.lower()
        full_url = url.lower()

        return {
            "url_length": min(len(full_url), 300),
            "has_https": int(full_url.startswith("https")),
            "has_at_symbol": int("@" in full_url),
            "has_ip": int(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", netloc) is not None),
            "has_dash": int("-" in netloc),
            "num_dots": netloc.count("."),
            "is_shortened": int(any(short in full_url for short in ["bit.ly", "tinyurl", "t.co", "is.gd", "buff.ly"])),
            "has_login_keyword": int(any(kw in path for kw in ["login", "signin", "verify", "account", "secure", "update"])),
            "subdomain_depth": max(0, len(netloc.split(".")) - 2),
            "is_known_safe_domain": int(any(domain in netloc for domain in KNOWN_SAFE_DOMAINS))
        }
    except Exception as e:
        print(f"⚠️ Feature extraction error for URL: {url} -> {e}")
        return None
