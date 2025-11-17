#!/usr/bin/env python3
"""
Quick Start Script for RentConnect-C3AN System
Run this to see the complete system in action
"""

import sys
import subprocess

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║         RENTCONNECT-C3AN SYSTEM QUICK START                ║
╚════════════════════════════════════════════════════════════╝

This system demonstrates:
✓ 10 specialized agents working together
✓ 3 complete workflows (Property Search, Roommate Matching, Tour Planning)
✓ Agent-to-agent data connections
✓ JSON-based agent registry

Choose an option:

[1] Run Full System Demo (all workflows)
[2] Run Agent Connection Examples
[3] View Agent Registry
[4] Run All

""")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🚀 Running Full System Demo...\n")
        subprocess.run([sys.executable, "system_implementation.py"])
    
    elif choice == "2":
        print("\n🔗 Running Agent Connection Examples...\n")
        subprocess.run([sys.executable, "agent_connections_example.py"])
    
    elif choice == "3":
        print("\n📋 Displaying Agent Registry...\n")
        import json
        with open('rentconnect_agent_registry.json', 'r') as f:
            registry = json.load(f)
        
        print(f"Registry Version: {registry['metadata']['version']}")
        print(f"Total Agents: {len(registry['agents'])}\n")
        
        for agent in registry['agents']:
            print(f"• {agent['name']} ({agent['id']})")
            print(f"  Description: {agent['description']}")
            print(f"  Capabilities: {', '.join(agent['capabilities'])}")
            print()
    
    elif choice == "4":
        print("\n🚀 Running Complete Demonstration...\n")
        subprocess.run([sys.executable, "system_implementation.py"])
        print("\n" + "="*60)
        subprocess.run([sys.executable, "agent_connections_example.py"])
    
    else:
        print("Invalid choice. Please run again and select 1-4.")

if __name__ == "__main__":
    main()
