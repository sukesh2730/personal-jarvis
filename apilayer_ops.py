"""
APILayer Integration Module for JARVIS

Provides access to 30+ production-grade REST APIs through a unified interface:
- Geocoding & Maps
- Email & Phone Validation
- Currency & Exchange Rates
- Flight & Travel Data
- Stock Market Data
- Web Scraping & Search
- Weather Data
- IP Geolocation
- And more...

All APIs use the same authentication model and base URL.
"""

import os
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class APILayerResponse:
    """Standard response wrapper for APILayer calls."""
    success: bool
    data: Any
    error: Optional[Dict[str, str]] = None


class APILayerOps:
    """APILayer unified suite operations manager for JARVIS."""
    
    BASE_URL = "https://api.apilayer.com"
    
    def __init__(self, access_key: Optional[str] = None):
        """
        Initialize APILayer operations.
        
        Args:
            access_key: APILayer access key (defaults to env var)
        """
        self.access_key = access_key or os.getenv("APILAYER_KEY")
        if not self.access_key or self.access_key in ["", "your_apilayer_key_here"]:
            self.available = False
        else:
            self.available = True
    
    def _make_request(self, product: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> APILayerResponse:
        """
        Make a request to APILayer API.
        
        Args:
            product: API product name (e.g., 'fixer', 'ipstack')
            endpoint: Endpoint path
            params: Additional query parameters
            
        Returns:
            APILayerResponse object
        """
        if not self.available:
            return APILayerResponse(
                success=False,
                data=None,
                error={"code": "missing_access_key", "message": "APILayer access key not configured"}
            )
        
        url = f"{self.BASE_URL}/{product}/{endpoint}"
        
        # Add access key to params
        if params is None:
            params = {}
        params['access_key'] = self.access_key
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            # Handle successful response
            if response.status_code == 200:
                data = response.json()
                
                # Check for legacy error format (ipstack, currencylayer, etc.)
                if isinstance(data, dict) and data.get('success') is False:
                    return APILayerResponse(
                        success=False,
                        data=None,
                        error=data.get('error', {"code": "unknown", "message": "API returned error"})
                    )
                
                return APILayerResponse(success=True, data=data)
            
            # Handle error response
            else:
                try:
                    error_data = response.json()
                    error_info = error_data.get('error', {})
                except:
                    error_info = {
                        "code": f"http_{response.status_code}",
                        "message": response.text or "Unknown error"
                    }
                
                return APILayerResponse(
                    success=False,
                    data=None,
                    error=error_info
                )
        
        except requests.Timeout:
            return APILayerResponse(
                success=False,
                data=None,
                error={"code": "timeout", "message": "Request timed out"}
            )
        except Exception as e:
            return APILayerResponse(
                success=False,
                data=None,
                error={"code": "exception", "message": str(e)}
            )
    
    # ========== Currency & Exchange Rates (Fixer) ==========
    
    def get_exchange_rates(self, base: str = "USD", symbols: Optional[str] = None) -> APILayerResponse:
        """
        Get latest currency exchange rates.
        
        Args:
            base: Base currency (e.g., 'USD', 'EUR')
            symbols: Comma-separated currency codes (e.g., 'GBP,JPY,CAD')
            
        Returns:
            APILayerResponse with exchange rate data
        """
        params = {"base": base}
        if symbols:
            params["symbols"] = symbols
        
        return self._make_request("fixer", "latest", params)
    
    def convert_currency(self, from_curr: str, to_curr: str, amount: float) -> APILayerResponse:
        """
        Convert amount between currencies.
        
        Args:
            from_curr: Source currency code
            to_curr: Target currency code
            amount: Amount to convert
            
        Returns:
            APILayerResponse with conversion result
        """
        params = {
            "from": from_curr,
            "to": to_curr,
            "amount": amount
        }
        return self._make_request("fixer", "convert", params)
    
    # ========== IP Geolocation (IPStack) ==========
    
    def geolocate_ip(self, ip: str) -> APILayerResponse:
        """
        Get geolocation data for an IP address.
        
        Args:
            ip: IP address to geolocate
            
        Returns:
            APILayerResponse with location data
        """
        return self._make_request("ipstack", ip, {})
    
    def get_own_ip_location(self) -> APILayerResponse:
        """
        Get geolocation data for current IP.
        
        Returns:
            APILayerResponse with location data
        """
        return self._make_request("ipstack", "check", {})
    
    # ========== Email Validation (Mailboxlayer) ==========
    
    def validate_email(self, email: str, smtp_check: bool = False) -> APILayerResponse:
        """
        Validate email address.
        
        Args:
            email: Email address to validate
            smtp_check: Whether to perform SMTP check (slower but more accurate)
            
        Returns:
            APILayerResponse with validation result
        """
        params = {"email": email}
        if smtp_check:
            params["smtp"] = 1
        
        return self._make_request("mailboxlayer", "check", params)
    
    # ========== Phone Validation (Numverify) ==========
    
    def validate_phone(self, number: str, country_code: Optional[str] = None) -> APILayerResponse:
        """
        Validate phone number.
        
        Args:
            number: Phone number to validate
            country_code: Optional 2-letter country code
            
        Returns:
            APILayerResponse with validation result
        """
        params = {"number": number}
        if country_code:
            params["country_code"] = country_code
        
        return self._make_request("numverify", "validate", params)
    
    # ========== Weather Data (Weatherstack) ==========
    
    def get_current_weather(self, location: str, units: str = "m") -> APILayerResponse:
        """
        Get current weather for a location.
        
        Args:
            location: City name, zip code, or coordinates
            units: 'm' for metric, 'f' for fahrenheit, 's' for scientific
            
        Returns:
            APILayerResponse with weather data
        """
        params = {
            "query": location,
            "units": units
        }
        return self._make_request("weatherstack", "current", params)
    
    # ========== Geocoding (Positionstack) ==========
    
    def geocode_address(self, address: str, limit: int = 1) -> APILayerResponse:
        """
        Convert address to coordinates.
        
        Args:
            address: Address string to geocode
            limit: Number of results to return
            
        Returns:
            APILayerResponse with coordinate data
        """
        params = {
            "query": address,
            "limit": limit
        }
        return self._make_request("positionstack", "forward", params)
    
    def reverse_geocode(self, lat: float, lon: float) -> APILayerResponse:
        """
        Convert coordinates to address.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            APILayerResponse with address data
        """
        params = {
            "query": f"{lat},{lon}"
        }
        return self._make_request("positionstack", "reverse", params)
    
    # ========== Flight Data (Aviationstack) ==========
    
    def get_flights(self, flight_iata: Optional[str] = None, 
                   dep_iata: Optional[str] = None,
                   arr_iata: Optional[str] = None) -> APILayerResponse:
        """
        Get flight information.
        
        Args:
            flight_iata: Flight number (e.g., 'AA100')
            dep_iata: Departure airport code
            arr_iata: Arrival airport code
            
        Returns:
            APILayerResponse with flight data
        """
        params = {}
        if flight_iata:
            params["flight_iata"] = flight_iata
        if dep_iata:
            params["dep_iata"] = dep_iata
        if arr_iata:
            params["arr_iata"] = arr_iata
        
        return self._make_request("aviationstack", "flights", params)
    
    # ========== VAT Validation (VATLayer) ==========
    
    def validate_vat(self, vat_number: str) -> APILayerResponse:
        """
        Validate VAT number.
        
        Args:
            vat_number: VAT number to validate
            
        Returns:
            APILayerResponse with validation result
        """
        params = {"vat_number": vat_number}
        return self._make_request("vatlayer", "validate", params)
    
    # ========== Language Detection (LanguageLayer) ==========
    
    def detect_language(self, text: str) -> APILayerResponse:
        """
        Detect language of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            APILayerResponse with language detection result
        """
        params = {"query": text}
        return self._make_request("languagelayer", "detect", params)
    
    # ========== Screen Capture (ScreenshotLayer) ==========
    
    def capture_screenshot(self, url: str, fullpage: bool = False, 
                          width: int = 1440) -> APILayerResponse:
        """
        Capture website screenshot.
        
        Args:
            url: URL to capture
            fullpage: Capture full page or just viewport
            width: Viewport width in pixels
            
        Returns:
            APILayerResponse with screenshot URL
        """
        params = {
            "url": url,
            "fullpage": 1 if fullpage else 0,
            "width": width
        }
        return self._make_request("screenshotlayer", "api/capture", params)
    
    # ========== PDF Generation (PDFLayer) ==========
    
    def html_to_pdf(self, document_url: str, page_size: str = "A4") -> APILayerResponse:
        """
        Convert HTML to PDF.
        
        Args:
            document_url: URL of HTML document
            page_size: Page size (A4, Letter, etc.)
            
        Returns:
            APILayerResponse with PDF URL
        """
        params = {
            "document_url": document_url,
            "page_size": page_size
        }
        return self._make_request("pdflayer", "api/convert", params)
    
    # ========== Bank Data (BankAPI) ==========
    
    def lookup_iban(self, iban: str) -> APILayerResponse:
        """
        Validate and lookup IBAN.
        
        Args:
            iban: IBAN to validate
            
        Returns:
            APILayerResponse with bank data
        """
        params = {"iban": iban}
        return self._make_request("bankapi", "validate", params)


def format_exchange_rates(response: APILayerResponse) -> str:
    """Format exchange rate data for display."""
    if not response.success:
        return f"Error: {response.error.get('message', 'Unknown error')}"
    
    data = response.data
    base = data.get('base', 'USD')
    date = data.get('date', 'N/A')
    rates = data.get('rates', {})
    
    lines = [f"\nExchange Rates (Base: {base}, Date: {date})\n"]
    for currency, rate in sorted(rates.items()):
        lines.append(f"  {currency}: {rate:.4f}")
    
    return "\n".join(lines)


def format_ip_location(response: APILayerResponse) -> str:
    """Format IP geolocation data for display."""
    if not response.success:
        return f"Error: {response.error.get('message', 'Unknown error')}"
    
    data = response.data
    lines = [
        f"\nIP Location Information:",
        f"  IP: {data.get('ip', 'N/A')}",
        f"  Location: {data.get('city', 'N/A')}, {data.get('region_name', 'N/A')}, {data.get('country_name', 'N/A')}",
        f"  Coordinates: {data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}",
        f"  Timezone: {data.get('timezone', {}).get('id', 'N/A')}",
        f"  ISP: {data.get('connection', {}).get('isp', 'N/A')}"
    ]
    
    return "\n".join(lines)


def format_weather(response: APILayerResponse) -> str:
    """Format weather data for display."""
    if not response.success:
        return f"Error: {response.error.get('message', 'Unknown error')}"
    
    data = response.data
    location = data.get('location', {})
    current = data.get('current', {})
    
    lines = [
        f"\nWeather for {location.get('name', 'N/A')}, {location.get('country', 'N/A')}",
        f"  Temperature: {current.get('temperature', 'N/A')}°C",
        f"  Feels Like: {current.get('feelslike', 'N/A')}°C",
        f"  Condition: {', '.join(current.get('weather_descriptions', ['N/A']))}",
        f"  Humidity: {current.get('humidity', 'N/A')}%",
        f"  Wind: {current.get('wind_speed', 'N/A')} km/h {current.get('wind_dir', '')}",
        f"  Pressure: {current.get('pressure', 'N/A')} mb",
        f"  UV Index: {current.get('uv_index', 'N/A')}"
    ]
    
    return "\n".join(lines)
