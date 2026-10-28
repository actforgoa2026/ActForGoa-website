"""Fixed phase policy; exported metadata is never execution authority."""

PIPELINE_VERSION = 'two_pass_v12'
EFFORT_POLICY = 'low_draft_high_reconstruction_v1'
BASE_CONFIG_EFFORT = 'medium'
_PHASE_EFFORTS = (('draft', 'low'), ('reconstruction', 'high'))


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
            'phase_efforts': dict(_PHASE_EFFORTS)}


def validate_policy_metadata(value):
    expected = phase_policy_metadata()
    if (not isinstance(value, dict) or 'effort' in value
            or any(value.get(key) != item for key, item in expected.items())):
        raise PhasePolicyError()


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
