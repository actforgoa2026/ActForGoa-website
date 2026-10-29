"""Reviewed text-only SDK pricing bounds; no accounting state."""
import json
MODEL = "claude-sonnet-5-5"
MAX_REQUEST_MICROUSD = ((160000+16384)*4+4096*10)*11//10+1

def request_bound(payload):
    # Standard Sonnet 5.5 rates checked 2026-10-29: $2/$10 per million.
    # Reserve at $4 input (covers 1h cache writes), $10 output, plus 10%.
    # UTF-8 bytes conservatively bound text tokens; include framing overhead.
    # Only text/custom tools are allowed; server tools/images have other charges.
    if payload.get('model')!=MODEL:raise ValueError('Unreviewed model')
    if any(k in payload for k in ('speed','service_tier')):raise ValueError('Unreviewed pricing tier')
    for t in payload.get('tools',[]):
        if t.get('type','custom')!='custom':raise ValueError('Server tools are disabled')
    def inspect(value):
        if isinstance(value,dict):
            if value.get('type') in ('image','document','container_upload'):raise ValueError('Only text evidence is supported')
            for item in value.values():inspect(item)
        elif isinstance(value,list):
            for item in value:inspect(item)
    inspect(payload)
    size=len(json.dumps(payload,ensure_ascii=False).encode())
    output=payload.get('max_tokens')
    if size>160000 or type(output) is not int or not 1<=output<=4096:raise ValueError('Provider request exceeds reviewed limits')
    return ((size+16384)*4+output*10)*11//10+1
