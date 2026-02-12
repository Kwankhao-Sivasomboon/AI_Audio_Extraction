
from typing import Optional
from pydantic import BaseModel, field_validator, ValidationInfo
import re

class CustomerInfo(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    license_plate: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return None
        # Rule: 10 digits, starts with 0
        clean_v = re.sub(r'\D', '', v)
        if len(clean_v) != 10 or not clean_v.startswith('0'):
            return None 
        return clean_v

    @field_validator('license_plate')
    @classmethod
    def validate_license_plate(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return None
        
        # Normalize: remove extra spaces
        v = v.strip()
        
        # Rule 1: NCC NNNN (1 digit, 2 thai chars, 1-4 digits)
        # Example: 1กข 1234 or 1กข1234
        pattern_1 = r'^[0-9][ก-ฮ]{2} ?[0-9]{1,4}$'
        
        # Rule 2: CC NNNN (2 thai chars, 0 digits (front), 1-4 digits (back))
        # Example: กข 1234 or กข1234
        pattern_2 = r'^[ก-ฮ]{2} ?[0-9]{1,4}$'
        
        # Rule 3: NN-NNNN (Truck) (2 digits, hyphen, 4 digits)
        # Example: 70-1234
        pattern_3 = r'^[0-9]{2}-[0-9]{4}$'
        
        if re.match(pattern_1, v) or re.match(pattern_2, v) or re.match(pattern_3, v):
            return v
            
        # If it matches the truck pattern without hyphen (6 digits), format it
        digit_pattern = r'^[0-9]{6}$'
        if re.match(digit_pattern, v):
            # Format as NN-NNNN
            return f"{v[:2]}-{v[2:]}"
            
        return None
