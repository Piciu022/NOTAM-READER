import re
import datetime

def parse_notam(raw_text):
    """
    Parses a raw NOTAM text string into a dictionary of fields.
    Standard ICAO NOTAM format:
    ID (Series/Year) NOTAMN/R/C
    Q) Qualifiers
    A) Location
    B) Start
    C) End
    D) Schedule (If present)
    E) Text
    F) Lower Limit
    G) Upper Limit
    """
    data = {
        'id': None,
        'type': None,
        'q_line': None,
        'location': None,
        'start_time': None,
        'end_time': None,
        'text': None,
        'lower_limit': None,
        'upper_limit': None,
        'raw_text': raw_text
    }

    # Clean whitespace
    text = raw_text.strip()

    # Extract ID (e.g., A1234/23)
    id_match = re.search(r'([A-Z]\d{4}/\d{2})\s+(NOTAM[NRC])', text)
    if id_match:
        data['id'] = id_match.group(1)
        raw_type = id_match.group(2)
        data['type'] = raw_type
        
        # Add human readable status
        if raw_type == 'NOTAMN':
            data['status'] = 'NEW'
        elif raw_type == 'NOTAMR':
            data['status'] = 'REPLACE'
        elif raw_type == 'NOTAMC':
            data['status'] = 'CANCEL'
        else:
            data['status'] = 'UNKNOWN'

    # Extract Fields
    
    # Q Line
    q_match = re.search(r'Q\)\s*(.*?)(?=\s*[A-G]\))', text, re.DOTALL)
    if q_match:
        data['q_line'] = q_match.group(1).strip()

    # A) Location
    a_match = re.search(r'A\)\s*([A-Z]{4})', text)
    if a_match:
        data['location'] = a_match.group(1)

    # B) Start Time (YYMMDDHHMM)
    b_match = re.search(r'B\)\s*(\d{10})', text)
    if b_match:
        data['start_time'] = b_match.group(1)

    # C) End Time (YYMMDDHHMM or PERM or EST)
    c_match = re.search(r'C\)\s*(\d{10}|PERM|EST)', text)
    if c_match:
        data['end_time'] = c_match.group(1)

    # E) Text
    # Captures everything after E) until the next field F) or G) or end of string
    e_match = re.search(r'E\)\s*(.*?)(?=\s*[FG]\)|$)', text, re.DOTALL)
    if e_match:
        data['text'] = e_match.group(1).strip()

    # F) Lower Limit
    f_match = re.search(r'F\)\s*(.*?)(?=\s*G\)|$)', text)
    if f_match:
        data['lower_limit'] = f_match.group(1).strip()
        
    # G) Upper Limit
    g_match = re.search(r'G\)\s*(.*)', text)
    if g_match:
        data['upper_limit'] = g_match.group(1).strip()

    return data

def decode_q_line(q_line):
    """
    Helper to decode the Q-line into human readable components.
    Format: Q) FIR/CODE/TRAFFIC/PURPOSE/SCOPE/LOWER/UPPER/COORDS/RADIUS
    TODO: Implement full decoding requiring a large dictionary of Q codes.
    For now, returns raw parts.
    """
    if not q_line:
        return {}
    
    parts = q_line.split('/')
    decoded = {
        'fir': parts[0] if len(parts) > 0 else None,
        'code': parts[1] if len(parts) > 1 else None,
        'traffic': parts[2] if len(parts) > 2 else None,
        'purpose': parts[3] if len(parts) > 3 else None,
        'scope': parts[4] if len(parts) > 4 else None,
        'lower': parts[5] if len(parts) > 5 else None,
        'upper': parts[6] if len(parts) > 6 else None,
        'coordinates': parts[7] if len(parts) > 7 else None,
        'radius': parts[8] if len(parts) > 8 else None,
    }
    return decoded
