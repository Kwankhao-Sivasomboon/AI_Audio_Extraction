
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
        # Remove any non-digit characters for checking except leading 0 if strictly required by rule
        # Rule: 10 digits, starts with 0
        clean_v = re.sub(r'\D', '', v)
        if len(clean_v) != 10 or not clean_v.startswith('0'):
            # Instead of raising validation error immediately which stops parsing, 
            # we might return None to signal invalid data if the goal is to flagged as incomplete.
            # But Pydantic usually raises validation errors. 
            # Let's verify requirement: "If any field is null or fails Rule-based -> Incomplete"
            # So returning None here (or letting it fail logic later) is one way.
            # However, typically validators correct format or raise error.
            # If we raise ValueError, Pydantic will not create the object model easily without try-except.
            # A better approach for "soft validation" might be allowing the field but marking as invalid elsewhere,
            # OR defining the field as strict and catching validation error at parsing time.
            # The prompt says: "If information is missing, Gemini returns null... Pydantic validates... if null or rule-based fail -> Incomplete"
            # So if rule fails, we should probably treat it as None (missing/invalid).
            return None 
            # raise ValueError("Phone number must be 10 digits and start with 0")
        return clean_v

    @field_validator('license_plate')
    @classmethod
    def validate_license_plate(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return None
        
        # Normalize: remove extra spaces
        v = v.strip()
        
        # Rule 1: NCC NNNN (1 digit, 2 thai chars, 1-4 digits)
        # Example: 1กข 1234
        pattern_1 = r'^[0-9][ก-ฮ]{2} [0-9]{1,4}$'
        
        # Rule 2: CC NNNN (2 thai chars, 0 digits (front), 1-4 digits (back))
        # Example: กข 1234
        pattern_2 = r'^[ก-ฮ]{2} [0-9]{1,4}$'
        
        # Rule 3: NN-NNNN (Truck) (2 digits, hyphen, 4 digits)
        # Example: 70-1234
        pattern_3 = r'^[0-9]{2}-[0-9]{4}$'
        
        if re.match(pattern_1, v) or re.match(pattern_2, v) or re.match(pattern_3, v):
            return v
            
        # If it matches the truck pattern without hyphen (6 digits), format it
        # "ถ้าด้านหน้าไม่มีตัวเลข ให้เป็นเลข 6 ตัว โดยตัวหน้า 2 ตัวหลัง 4" -> This part of rule is slightly ambiguous.
        # It likely means input might be "701234", verify if it's 6 digits and valid truck prefix? 
        # But usually truck plates are 70-xxxx.
        # Let's assume if we get 6 digits, we format it.
        digit_pattern = r'^[0-9]{6}$'
        if re.match(digit_pattern, v):
            # Format as NN-NNNN
            return f"{v[:2]}-{v[2:]}"
            
        return None # Invalid format
