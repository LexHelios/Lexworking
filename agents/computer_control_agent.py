#!/usr/bin/env python3
"""
Computer Control Agent for OMNIPOTENT System
"""

from omnipotent_agents.computer_control_agent import ComputerControlAgent as BaseComputerControlAgent

class ComputerControlAgent(BaseComputerControlAgent):
    """Wrapper for compatibility with original omnipotent system"""
    
    def __init__(self, config):
        super().__init__(config)