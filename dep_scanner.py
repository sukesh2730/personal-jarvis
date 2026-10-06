"""
Dependency Scanner for JARVIS - Phase 3
Scans dependencies for vulnerabilities using pip-audit.
"""
import subprocess
import json
import os
from typing import Dict, List, Optional
from pathlib import Path


def scan_dependencies(requirements_path: str = "./requirements.txt") -> Dict:
    """
    Scan requirements.txt using pip-audit.
    
    Args:
        requirements_path: Path to requirements.txt
        
    Returns:
        Dict with 'vulnerabilities' and 'outdated' lists
    """
    if not os.path.exists(requirements_path):
        return {
            "error": f"Requirements file not found: {requirements_path}",
            "vulnerabilities": [],
            "outdated": []
        }
    
    try:
        # Run pip-audit with JSON output
        result = subprocess.run(
            ["pip-audit", "--requirement", requirements_path, "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse JSON output
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                return parse_audit_results(data)
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw output
                return {
                    "error": "Could not parse pip-audit output",
                    "raw_output": result.stdout,
                    "vulnerabilities": [],
                    "outdated": []
                }
        else:
            # No vulnerabilities found
            return {
                "vulnerabilities": [],
                "outdated": [],
                "message": "No vulnerabilities found, sir."
            }
    
    except FileNotFoundError:
        return {
            "error": "pip-audit not installed. Install with: pip install pip-audit",
            "vulnerabilities": [],
            "outdated": []
        }
    except subprocess.TimeoutExpired:
        return {
            "error": "Scan timed out after 60 seconds",
            "vulnerabilities": [],
            "outdated": []
        }
    except Exception as e:
        return {
            "error": f"Scan failed: {str(e)}",
            "vulnerabilities": [],
            "outdated": []
        }


def parse_audit_results(data: Dict) -> Dict:
    """
    Parse pip-audit JSON output.
    
    Args:
        data: JSON data from pip-audit
        
    Returns:
        Structured vulnerability data
    """
    vulnerabilities = []
    
    # pip-audit format: list of dependencies with vulnerabilities
    dependencies = data.get("dependencies", [])
    
    for dep in dependencies:
        name = dep.get("name", "unknown")
        version = dep.get("version", "unknown")
        vulns = dep.get("vulns", [])
        
        for vuln in vulns:
            vulnerabilities.append({
                "package": name,
                "current_version": version,
                "cve_id": vuln.get("id", "N/A"),
                "severity": vuln.get("severity", "UNKNOWN"),
                "description": vuln.get("description", "No description"),
                "fixed_versions": vuln.get("fix_versions", [])
            })
    
    return {
        "vulnerabilities": vulnerabilities,
        "outdated": [],  # pip-audit doesn't track outdated packages
        "total_vulnerabilities": len(vulnerabilities)
    }


def format_scan_results(results: Dict) -> str:
    """
    Format scan results for console display.
    
    Args:
        results: Results from scan_dependencies
        
    Returns:
        Formatted string
    """
    lines = []
    lines.append("=" * 60)
    lines.append("DEPENDENCY VULNERABILITY SCAN")
    lines.append("=" * 60)
    lines.append("")
    
    # Check for errors
    if "error" in results:
        lines.append(f"Error: {results['error']}")
        if "raw_output" in results:
            lines.append("")
            lines.append("Raw output:")
            lines.append(results['raw_output'])
        return "\n".join(lines)
    
    # Check for message (no vulnerabilities)
    if "message" in results:
        lines.append(results['message'])
        return "\n".join(lines)
    
    vulnerabilities = results.get("vulnerabilities", [])
    
    if not vulnerabilities:
        lines.append("✓ No vulnerabilities found, sir. All dependencies are secure.")
        return "\n".join(lines)
    
    # Display vulnerabilities
    lines.append(f"Found {len(vulnerabilities)} vulnerabilities:")
    lines.append("")
    
    for vuln in vulnerabilities:
        lines.append(f"Package: {vuln['package']}")
        lines.append(f"Current Version: {vuln['current_version']}")
        lines.append(f"CVE ID: {vuln['cve_id']}")
        lines.append(f"Severity: {vuln['severity']}")
        
        if vuln['fixed_versions']:
            fixed = ", ".join(vuln['fixed_versions'])
            lines.append(f"Fixed in: {fixed}")
        else:
            lines.append("Fixed in: No fix available yet")
        
        lines.append(f"Description: {vuln['description'][:100]}...")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append("")
    lines.append("Recommendation: Update vulnerable packages with:")
    lines.append("pip install --upgrade [package_name]")
    
    return "\n".join(lines)


def check_outdated_packages() -> List[Dict]:
    """
    Check for outdated packages using pip list --outdated.
    
    Returns:
        List of outdated packages
    """
    try:
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            return json.loads(result.stdout)
        return []
    except Exception:
        return []


def format_outdated_packages(outdated: List[Dict]) -> str:
    """
    Format outdated packages for display.
    
    Args:
        outdated: List of outdated package dicts
        
    Returns:
        Formatted string
    """
    if not outdated:
        return "All packages are up to date, sir."
    
    lines = []
    lines.append("Outdated packages (no known vulnerabilities):")
    lines.append("")
    
    for pkg in outdated:
        name = pkg.get("name", "unknown")
        current = pkg.get("version", "unknown")
        latest = pkg.get("latest_version", "unknown")
        lines.append(f"  {name}: {current} → {latest}")
    
    return "\n".join(lines)
