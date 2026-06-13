"""
SEVAGOTH Virus Scanner Module
Handles file scanning, threat detection, and security analysis
"""

import hashlib
import json
import os
import re
from config import (
    THREAT_DB_FILE, SUSPICIOUS_PATTERNS, CRITICAL_PATHS, DEFAULT_THREATS
)


class VirusScanner:
    """Main virus scanner class for security analysis"""
    
    def __init__(self):
        self.threat_db_file = THREAT_DB_FILE
        self.threat_database = {}
        self.suspicious_patterns = SUSPICIOUS_PATTERNS
        self.critical_paths = CRITICAL_PATHS

    def load_threat_database(self):
        """Load threat database from JSON file"""
        if os.path.exists(self.threat_db_file):
            with open(self.threat_db_file, "r") as f:
                self.threat_database = json.load(f)
        else:
            # Use default threats from config
            self.threat_database = DEFAULT_THREATS.copy()
            self.save_threat_database()
        print(f"[SEVAGOTH SCANNER] Threat database loaded: {len(self.threat_database)} known threats.")

    def save_threat_database(self):
        """Save threat database to JSON file"""
        with open(self.threat_db_file, "w") as f:
            json.dump(self.threat_database, f, indent=4)
        print("[SEVAGOTH SCANNER] Threat database saved.")

    def _hash_file(self, filepath: str) -> str:
        """
        Calculate MD5 hash of a file
        
        Args:
            filepath: Path to the file to hash
            
        Returns:
            MD5 hash as hexadecimal string
        """
        hasher = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def _scan_file_for_patterns(self, filepath: str) -> list:
        """
        Scan file for suspicious code patterns
        
        Args:
            filepath: Path to the file to scan
            
        Returns:
            List of matching patterns found
        """
        matches = []
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            for pattern in self.suspicious_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    matches.append({"pattern": pattern, "file": filepath})
        except Exception:
            pass
        return matches

    def _check_file_permissions(self, filepath: str) -> dict:
        """
        Check file permissions for suspicious settings
        
        Args:
            filepath: Path to the file
            
        Returns:
            Dictionary with permission information
        """
        try:
            stat_info = os.stat(filepath)
            return {
                "readable": bool(stat_info.st_mode & 0o400),
                "writable": bool(stat_info.st_mode & 0o200),
                "executable": bool(stat_info.st_mode & 0o100)
            }
        except:
            return {}

    def scan_file(self, filepath: str) -> dict:
        """
        Complete scan of a single file
        
        Args:
            filepath: Path to the file to scan
            
        Returns:
            Dictionary with scan results
        """
        result = {
            "file": filepath,
            "threat": None,
            "suspicious_patterns": [],
            "permission_issues": []
        }
        
        # Check file hash against threat database
        file_hash = self._hash_file(filepath)
        if file_hash and file_hash in self.threat_database:
            result["threat"] = self.threat_database[file_hash]
        
        # Scan code files for suspicious patterns
        if filepath.endswith((".py", ".js", ".bat", ".ps1", ".vbs", ".sh")):
            result["suspicious_patterns"] = self._scan_file_for_patterns(filepath)
        
        # Check file permissions
        perms = self._check_file_permissions(filepath)
        if perms.get("executable") and filepath.endswith((".exe", ".dll", ".scr")):
            result["permission_issues"].append(f"Executable file detected: {filepath}")
        
        return result

    def scan_directory(self, directory: str) -> dict:
        """
        Recursively scan directory for threats
        
        Args:
            directory: Path to the directory to scan
            
        Returns:
            Dictionary with scan results for entire directory
        """
        results = {
            "directory": directory,
            "scanned": 0,
            "threats_found": 0,
            "threats": [],
            "suspicious_files": [],
            "permission_alerts": [],
            "error": None
        }
        
        if not os.path.exists(directory):
            results["error"] = f"Directory '{directory}' does not exist."
            return results
        
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories and system directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in
                       ('$Recycle.Bin', 'System Volume Information')]
            
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    file_result = self.scan_file(filepath)
                    results["scanned"] += 1
                    
                    # Check for threats
                    if file_result["threat"]:
                        results["threats_found"] += 1
                        results["threats"].append({
                            "file": filepath,
                            "threat": file_result["threat"]
                        })
                    
                    # Check for suspicious patterns
                    if file_result["suspicious_patterns"]:
                        results["suspicious_files"].append({
                            "file": filepath,
                            "patterns": file_result["suspicious_patterns"]
                        })
                    
                    # Check for permission issues
                    if file_result["permission_issues"]:
                        results["permission_alerts"].append({
                            "file": filepath,
                            "issues": file_result["permission_issues"]
                        })
                except Exception:
                    continue
        
        return results

    def run_emergency_scan(self) -> dict:
        """
        Scan critical system paths
        
        Returns:
            Dictionary with results from all critical paths
        """
        all_results = {}
        for path in self.critical_paths:
            if os.path.exists(path):
                print(f"[SEVAGOTH SCANNER] Scanning: {path}")
                all_results[path] = self.scan_directory(path)
        return all_results

    def add_threat(self, file_hash: str, threat_name: str):
        """
        Add new threat to database
        
        Args:
            file_hash: MD5 hash of the threat
            threat_name: Name/description of the threat
        """
        self.threat_database[file_hash] = threat_name
        self.save_threat_database()
        print(f"[SEVAGOTH SCANNER] Threat added: {threat_name} ({file_hash})")


def sevagoth_virus_check_command(query: str) -> str:
    """
    Execute virus scan based on voice command
    
    Args:
        query: The user's voice command
        
    Returns:
        String report of scan results
    """
    scanner = VirusScanner()
    scanner.load_threat_database()
    
    # Check for special scan commands
    if "database" in query:
        scanner.save_threat_database()
        return "Threat database saved."
    
    if "emergency" in query:
        results = scanner.run_emergency_scan()
        return f"Emergency scan complete. Checked {len(results)} critical paths."
    
    # Extract directory from query
    match = re.search(r'in (.+)', query)
    target_dir = match.group(1).strip().strip('"').strip("'") if match else os.getcwd()
    
    # Scan the directory
    results = scanner.scan_directory(target_dir)
    
    if results.get("error"):
        return results["error"]
    
    # Build report
    report = (f"Scan complete for {target_dir}:\n"
              f"- Files scanned: {results['scanned']}\n"
              f"- Threats found: {results['threats_found']}\n"
              f"- Suspicious files: {len(results['suspicious_files'])}\n"
              f"- Permission alerts: {len(results['permission_alerts'])}\n")
    
    if results['threats']:
        report += "\nTHREATS DETECTED:\n"
        for threat in results['threats']:
            report += f"  ⚠️  {threat['file']}: {threat['threat']}\n"
    
    if results['suspicious_files']:
        report += "\nSUSPICIOUS PATTERNS:\n"
        for susp in results['suspicious_files'][:3]:
            report += f"  🔍 {susp['file']}\n"
            for pat in susp['patterns']:
                report += f"     Pattern: {pat['pattern']}\n"
    
    if results['permission_alerts']:
        report += "\nPERMISSION ALERTS:\n"
        for alert in results['permission_alerts'][:3]:
            report += f"  🔐 {alert['file']}\n"
            for issue in alert['issues']:
                report += f"     {issue}\n"
    
    return report