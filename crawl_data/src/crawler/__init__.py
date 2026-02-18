"""
src/crawler/

Package crawler — fetch và parse product data.
"""

from .fetcher import Fetcher
from .parser import Parser
from .link_discovery import LinkDiscovery

__all__ = ["Fetcher", "Parser", "LinkDiscovery"]