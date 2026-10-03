import random
import string

def js_hash(s):
    hash_val = 0
    for char in s:
        char_code = ord(char)
        # JS: hash = ((hash << 5) - hash) + char_code
        # We need to emulate 32-bit signed integer behavior for the shift and subtraction
        
        # 1. Cast current hash to int32 for the shift
        h32 = hash_val & 0xFFFFFFFF
        if h32 > 0x7FFFFFFF: h32 -= 0x100000000
        
        # 2. Perform shift and subtract
        # (h32 << 5) is also int32
        term = (h32 << 5) & 0xFFFFFFFF
        if term > 0x7FFFFFFF: term -= 0x100000000
        
        term = term - h32
        # Result of subtraction is int32
        
        # 3. Add char_code (JS addition results in double, but we only care about int32 for next iter)
        # Actually, in the JS code: hash = charCode + term.
        # The result 'hash' is stored as a number.
        # In the next iteration, it is cast to int32 again.
        
        hash_val = term + char_code
        
        # Note: In JS, hash can grow beyond 32-bit here, but it's cast back in the next loop.
        # However, for the FINAL score calculation: (Math.abs(hash) % 600) + 300
        # We need the final 'hash' value.
        # Does the final hash value stay within 32-bit? 
        # If the string is short, maybe. If long, it might overflow 32-bit float precision? Unlikely for PAN.
        # But wait, 'hash' is a standard JS number (double).
        # The bitwise ops return int32.
        # So 'term' is int32. 'char_code' is small.
        # So 'hash_val' is roughly int32 range.
        
    return hash_val

def get_score(pan):
    h = js_hash(pan)
    # JS: Math.abs(hash)
    return (abs(h) % 600) + 300

def find_pans():
    # Format: 5 chars, 4 digits, 1 char
    # e.g., ABCDE1234F
    
    targets = {
        "Low (< 500)": [],
        "Medium (600-700)": [],
        "High (> 750)": []
    }
    
    prefixes = ["ABCDE", "FGHIJ", "KLMNO"]
    suffixes = string.ascii_uppercase
    
    print("Searching for PANs...")
    
    count = 0
    while any(len(v) < 3 for v in targets.values()) and count < 100000:
        prefix = random.choice(prefixes)
        digits = f"{random.randint(1000, 9999)}"
        suffix = random.choice(suffixes)
        pan = f"{prefix}{digits}{suffix}"
        
        score = get_score(pan)
        
        if score < 500 and len(targets["Low (< 500)"]) < 3:
            targets["Low (< 500)"].append((pan, score))
        elif 600 <= score < 700 and len(targets["Medium (600-700)"]) < 3:
            targets["Medium (600-700)"].append((pan, score))
        elif score > 750 and len(targets["High (> 750)"]) < 3:
            targets["High (> 750)"].append((pan, score))
            
        count += 1
        
    with open("pans.txt", "w") as f:
        f.write("-" * 30 + "\n")
        for category, items in targets.items():
            f.write(f"{category}:\n")
            for pan, score in items:
                f.write(f"  PAN: {pan} | Score: {score}\n")
        f.write("-" * 30 + "\n")
    print("Done writing to pans.txt")

if __name__ == "__main__":
    find_pans()
