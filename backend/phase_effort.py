"""Fixed phase policy; exported metadata is never execution authority."""

PIPELINE_VERSION = 'single_final_v1'
EFFORT_POLICY = 'single_final_high_v1'
BASE_CONFIG_EFFORT = 'medium'
_PHASE_EFFORTS = (('reconstruction', 'high'),)
_EMPTY_PLAN_UTF8 = '{"status":"insufficient_evidence","points":[],"units":[]}'


def local_plan_adapter():
    """Fresh local no-plan input, never a generated evidence assessment."""
    import json
    return json.loads(_EMPTY_PLAN_UTF8)


def validate_local_plan_adapter(value):
    import json
    if (type(value) is not dict or json.dumps(value, ensure_ascii=False, separators=(',', ':')) != _EMPTY_PLAN_UTF8):
        raise PhasePolicyError()


def execution_metadata():
    import hashlib
    return {'provider_call_count': 1, 'plan_input_mode': 'no_generated_plan_empty_adapter_v1',
            'local_adapter': {'value': local_plan_adapter(),
                'sha256': hashlib.sha256(_EMPTY_PLAN_UTF8.encode()).hexdigest(),
                'provenance': {'plan_origin': 'local_empty', 'generated_plan': False}}}


class PhasePolicyError(ValueError):
    def __init__(self):
        super().__init__('Invalid answer phase policy')


def phase_effort(phase):
    for name, effort in _PHASE_EFFORTS:
        if type(phase) is str and phase == name:
            return effort
    raise PhasePolicyError()


def phase_policy_metadata():
    """Return detached JSON values, including a fresh nested phase map."""
    return {'base_config_effort': BASE_CONFIG_EFFORT, 'effort_policy': EFFORT_POLICY,
            'phase_efforts': dict(_PHASE_EFFORTS), **execution_metadata()}


def validate_policy_metadata(value):
    import json
    expected = phase_policy_metadata()
    try:
        if (not isinstance(value, dict) or 'effort' in value
                or type(value.get('provider_call_count')) is not int
                or any(json.dumps(value.get(key), sort_keys=True, allow_nan=False) !=
                       json.dumps(item, sort_keys=True, allow_nan=False) for key, item in expected.items())):
            raise PhasePolicyError()
    except (TypeError, ValueError):
        raise PhasePolicyError() from None


def validate_pipeline_config(config):
    if type(config.max_output_tokens) is not int or (config.pipeline, config.provider, config.model, config.effort, config.max_output_tokens) != (
            PIPELINE_VERSION, 'anthropic', 'claude-haiku-5-5', BASE_CONFIG_EFFORT, 12000):
        raise PhasePolicyError()


def check_phase_request(body, *, pipeline_version, effort_policy, base_config_effort, phase):
    """Check trusted local context against the actual request before I/O."""
    if (pipeline_version != PIPELINE_VERSION or effort_policy != EFFORT_POLICY
            or base_config_effort != BASE_CONFIG_EFFORT):
        raise PhasePolicyError()
    expected = phase_effort(phase)
    if (not isinstance(body, dict) or not isinstance(body.get('output_config'), dict)
            or body.get('model') != 'claude-haiku-5-5'
            or type(body.get('max_tokens')) is not int or body['max_tokens'] != 12000
            or body['output_config'].get('effort') != expected):
        raise PhasePolicyError()
