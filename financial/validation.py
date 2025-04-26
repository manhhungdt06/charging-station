from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path
from .core import ChargerConfig

@dataclass
class SpaceRequirements:
    parking_length: float = 5000  # mm
    parking_width: float = 2500   # mm
    total_length: float = 5400   # mm
    min_spacing: float = 2271     # mm between chargers
    safety_margin: float = 1000   # mm safety buffer
    transformer_area: float = 20000000  # mm² for transformer
    auxiliary_space: float = 30000000  # mm² for other equipment

@dataclass
class SafetyRequirements:
    pccc_certified: bool = False
    input_voltage_compliant: bool = False
    protection_features: List[str] = None
    ip_rating: str = None
    emergency_stop: bool = True
    ground_fault_protection: bool = True
    overcurrent_protection: bool = True
    temperature_monitoring: bool = True
    cable_management: bool = True

class StationValidator:
    def __init__(self, config_path: str = "vinfast-charger.json"):
        self.charger_configs = self._load_charger_configs(config_path)
        self.space_reqs = SpaceRequirements()
    
    def _load_charger_configs(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return {c['name']: c for c in json.load(f)}
        except FileNotFoundError:
            raise FileNotFoundError(f"Charger config file not found: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in config file: {config_path}")
    
    def validate_space_requirements(
        self,
        charger_configs: List[ChargerConfig],
        mounting_type: str
    ) -> Dict:
        if not charger_configs:
            raise ValueError("No charger configurations provided")
        
        space_per_spot = self.space_reqs.total_length * self.space_reqs.parking_width
        
        # Use spacing based on mounting type
        spacing = {
            "wall": 4000,
            "side": 900,
            "rear": 1150
        }.get(mounting_type, self.space_reqs.min_spacing)
        
        if mounting_type not in ["wall", "side", "rear"]:
            raise ValueError(f"Invalid mounting type: {mounting_type}")
        
        total_spots = sum(config.quantity for config in charger_configs)
        
        # Calculate total dimensions with safety margins
        total_width = (self.space_reqs.parking_width * total_spots) + \
                     (spacing * (total_spots - 1)) + \
                     (2 * self.space_reqs.safety_margin)
        
        total_length = self.space_reqs.total_length + self.space_reqs.safety_margin
        
        total_power = sum(config.power * config.quantity for config in charger_configs)
        
        # Calculate required areas
        parking_area = total_width * total_length
        transformer_area = self.space_reqs.transformer_area if total_power > 560 else 0
        auxiliary_area = self.space_reqs.auxiliary_space
        
        total_area = (parking_area + transformer_area + auxiliary_area) / 1_000_000
        
        return {
            'required_area': round(total_area, 2),
            'space_per_charger': round(space_per_spot / 1_000_000, 2),
            'total_width': round(total_width / 1000, 2),
            'total_length': round(total_length / 1000, 2),
            'needs_transformer': total_power > 560,
            'parking_area': round(parking_area / 1_000_000, 2),
            'transformer_area': round(transformer_area / 1_000_000, 2),
            'auxiliary_area': round(auxiliary_area / 1_000_000, 2)
        }
    
    def validate_safety_requirements(self, charger_configs: List[ChargerConfig]) -> List[Dict]:
        results = []
        
        for config in charger_configs:
            if config.type_name not in self.charger_configs:
                raise ValueError(f"Unknown charger type: {config.type_name}")
            
            charger = self.charger_configs[config.type_name]
            
            protection = charger['protection'].split('/')
            ip_rating = next((p for p in protection if p.startswith('IP')), None)
            
            safety = SafetyRequirements(
                pccc_certified=True,
                input_voltage_compliant=charger['input_voltage'].startswith('3 pha, 400VAC'),
                protection_features=[p for p in protection if not p.startswith('IP')],
                ip_rating=ip_rating
            )
            
            results.append({
                'charger_type': config.type_name,
                'quantity': config.quantity,
                'safety': safety
            })
        
        return results
    
    def validate_charger_configuration(
        self,
        charger_configs: List[ChargerConfig],
        mounting_type: str
    ) -> Dict:
        if not charger_configs:
            raise ValueError("No charger configurations provided")
        
        space_validation = self.validate_space_requirements(charger_configs, mounting_type)
        safety_results = self.validate_safety_requirements(charger_configs)
        total_power = sum(config.power * config.quantity for config in charger_configs)
        transformer_capacity = 560
        
        all_safety_compliant = all(
            result['safety'].pccc_certified and
            result['safety'].input_voltage_compliant
            for result in safety_results
        )
        
        return {
            'space_validation': space_validation,
            'safety_validation': safety_results,
            'power_requirements': {
                'total_power': total_power,
                'needs_additional_transformer': total_power > transformer_capacity,
                'transformer_capacity': transformer_capacity
            },
            'is_valid_configuration': all_safety_compliant
        }
