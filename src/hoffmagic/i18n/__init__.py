"""Internationalization (i18n) module for hoffmagic.

This module provides a structured system for handling translations in the application.
It separates translations by domain and provides a unified interface for accessing
translations with proper fallbacks.
"""
from typing import Dict, Optional, Any, List, Union
import logging
from pathlib import Path
import json
import os

from .languages import LANGUAGES, DEFAULT_LANGUAGE, Language

# Setup logger
logger = logging.getLogger("hoffmagic.i18n")

class TranslationKey:
    """Class for handling string interpolation in translations."""
    
    def __init__(self, key: str, default: Optional[str] = None):
        self.key = key
        self.default = default

    def format(self, **kwargs: Any) -> str:
        """Format the translation with the given kwargs."""
        try:
            return self.default.format(**kwargs) if self.default else self.key
        except KeyError as e:
            logger.warning(f"Missing format key {e} for translation {self.key}")
            return self.default or self.key
        except Exception as e:
            logger.error(f"Error formatting translation {self.key}: {e}")
            return self.default or self.key


class TranslationDomain:
    """Represents a domain of translations (e.g., 'common', 'blog', 'contact')."""
    
    def __init__(self, name: str, translations: Dict[str, str]):
        self.name = name
        self.translations = translations

    def get(self, key: str, default: Optional[str] = None) -> Union[str, TranslationKey]:
        """Get a translation by key with fallback to default."""
        if key in self.translations:
            return self.translations[key]
        if default is not None:
            return default
        # Return the key itself as fallback
        return key

    def __getattr__(self, key: str) -> str:
        """Allow accessing translations as attributes."""
        return self.get(key, key)


class TranslationManager:
    """Manages translations for the application across multiple domains and languages."""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, Dict[str, str]]] = {}
        self.domains: List[str] = []
        self._load_translations()

    def _load_translations(self) -> None:
        """Load all translation files from the i18n directory."""
        # Get the directory containing translation files
        i18n_dir = Path(__file__).parent
        
        # For each language
        for lang_code in LANGUAGES:
            if lang_code not in self.translations:
                self.translations[lang_code] = {}
            
            # Load each domain file
            domain_dir = i18n_dir / lang_code
            if not domain_dir.exists():
                logger.warning(f"No translations directory for language {lang_code}")
                continue
                
            for domain_file in domain_dir.glob("*.json"):
                domain_name = domain_file.stem
                if domain_name not in self.domains:
                    self.domains.append(domain_name)
                
                try:
                    with open(domain_file, "r", encoding="utf-8") as f:
                        domain_translations = json.load(f)
                        self.translations[lang_code][domain_name] = domain_translations
                except Exception as e:
                    logger.error(f"Error loading translations for {lang_code}/{domain_name}: {e}")
                    self.translations[lang_code][domain_name] = {}

    def get_domain(self, lang: str, domain: str) -> TranslationDomain:
        """Get a translation domain for a specific language."""
        if lang not in self.translations:
            logger.warning(f"Language {lang} not found, falling back to {DEFAULT_LANGUAGE}")
            lang = DEFAULT_LANGUAGE
        
        if domain not in self.translations[lang]:
            logger.warning(f"Domain {domain} not found for language {lang}")
            return TranslationDomain(domain, {})
        
        return TranslationDomain(domain, self.translations[lang][domain])

    def get_all_domains(self, lang: str) -> Dict[str, TranslationDomain]:
        """Get all translation domains for a specific language."""
        domains = {}
        if lang not in self.translations:
            logger.warning(f"Language {lang} not found, falling back to {DEFAULT_LANGUAGE}")
            lang = DEFAULT_LANGUAGE
            
        for domain in self.domains:
            domains[domain] = self.get_domain(lang, domain)
        
        return domains


class I18n:
    """Main internationalization class that provides translations for templates."""
    
    def __init__(self, lang: str):
        self.lang = lang if lang in LANGUAGES else DEFAULT_LANGUAGE
        self.manager = TranslationManager()
        self.domains = self.manager.get_all_domains(self.lang)
    
    def get(self, key: str, default: Optional[str] = None, domain: str = "common") -> str:
        """Get a translation by key with optional domain and default value."""
        # Check if the key contains a domain prefix (domain:key)
        if ":" in key:
            domain_name, key = key.split(":", 1)
            if domain_name in self.domains:
                domain = domain_name
        
        # Get from specific domain if exists
        if domain in self.domains:
            return self.domains[domain].get(key, default)
            
        # Fallback: try in every domain
        for domain_obj in self.domains.values():
            value = domain_obj.get(key, None)
            if value != key:  # Found a non-fallback value
                return value
                
        # Final fallback
        return default if default is not None else key
    
    def __getattr__(self, key: str) -> str:
        """Allow accessing common translations as attributes."""
        if "common" in self.domains:
            return self.domains["common"].get(key, key)
        return key
    
    def format(self, key: str, default: Optional[str] = None, domain: str = "common", **kwargs: Any) -> str:
        """Get a translation and format it with the given kwargs."""
        translation = self.get(key, default, domain)
        try:
            return translation.format(**kwargs)
        except (AttributeError, KeyError, ValueError) as e:
            logger.warning(f"Error formatting translation '{key}': {e}")
            return translation


# Singleton instance of the translation manager
_manager = TranslationManager()

def get_translations(lang: str) -> I18n:
    """Get translations for a specific language."""
    return I18n(lang)

def get_available_languages() -> List[Language]:
    """Get all available languages."""
    return [LANGUAGES[code] for code in LANGUAGES]