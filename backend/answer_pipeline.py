"""Shared two-phase execution for HTTP and acceptance, with no implicit retries."""
import asyncio
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import time
import uuid

from .anthropic_provider import API_VERSION, INPUT_ALLOWANCE, AnthropicAPIError, message_request
from .answer_trace import outgoing_request_capture, final_json_capture
from .chat import MAX_PROMPT_BYTES, FRAMING_TOKEN_ALLOWANCE
from .reconstruction import (PIPELINE_VERSION, pipeline_spec, CORRECTION_PROMPT_BYTES,
    PROVIDER_DEADLINE_SECONDS, PROVIDER_STAGE_SECONDS, prepare_reconstruction,
    reconstruction_message_request, normalize_reconstruction, encoded, digest)
from .source_spans import ANCHOR_PROTOCOL, verify_annotated_payload, verify_wire_binding
from .span_draft import prepare_span_draft, span_draft_message_request, normalize_span_draft
from .paragraph_slots import PARAGRAPH_PROTOCOL, AnswerEnvelopeError
from .evidence_plan import PLAN_PROTOCOL, FINAL_INTERNAL_PROTOCOL
from .phase_effort import (EFFORT_POLICY, PhasePolicyError, phase_effort, phase_policy_metadata,
                           validate_pipeline_config, check_phase_request)


class PipelineFailure(Exception):
    """Only a fixed local category is public/loggable; trace is separately owned."""
    def __init__(self, code, trace, status_code=None):
        self.code, self.trace, self.status_code = code, trace, status_code
        super().__init__(code)


@dataclass
class PipelineResult:
    answer: dict
    trace: dict


def utc_day():
    return datetime.now(timezone.utc).date().isoformat()


def pair_maximum_cost(config):
    return sum(pair_maximum_costs(config))


def pair_maximum_costs(config):
    return [config.maximum_cost_microusd(MAX_PROMPT_BYTES + FRAMING_TOKEN_ALLOWANCE),
            config.maximum_cost_microusd(CORRECTION_PROMPT_BYTES + FRAMING_TOKEN_ALLOWANCE)]


def usage_within_bound(stage):
    usage = stage.get('reported_usage', {})
    keys = ('input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens')
    if not all(type(usage.get(k)) is int and usage[k] >= 0 for k in keys):
        return False
    return (usage['input_tokens'] + usage['cache_creation_input_tokens'] + usage['cache_read_input_tokens']
            <= stage['reserved_input_tokens'] and usage['output_tokens'] <= stage['reserved_output_tokens']
            and usage['cache_creation_input_tokens'] == 0)


def initial_pipeline_trace(parent_id, expected_day):
    return {'capture_version': pipeline_spec()['capture_version'], 'pipeline_spec': pipeline_spec(),
            **phase_policy_metadata(), 'parent_id': parent_id, 'expected_day': expected_day,
            'status': 'not_started', 'phases': [
                {'phase': name, 'state': 'not_started', 'provider_attempts': 0,
                 'effort_policy': EFFORT_POLICY, 'expected_phase_effort': phase_effort(name),
                 'outgoing_request': {'capture_status': 'not_dispatched'}}
                for name in ('draft', 'reconstruction')]}


async def joined_native_call(function):
    """Do not abandon an owned non-cancellable native call on task cancellation.

    This deliberately can outlive a client/deadline. It starts no provider work;
    callers recheck disconnection and elapsed time after the worker is quiescent.
    """
    task = asyncio.create_task(asyncio.to_thread(function))
    cancelled = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            cancelled = True
    if cancelled:
        # Retrieve any worker exception without exposing it during cancellation.
        if not task.cancelled():
            task.exception()
        raise asyncio.CancelledError()
    return task.result()


async def run_answer_pipeline(request, prepared, config, *, limits, client_factory,
                              observer=None, request_started_at=None, request_id=None,
                              expected_day=None, disconnected=None):
    """Return only a corrected final answer; preserve every committed reservation.

    Retrieval happens in its original owner before this entry point. Its elapsed
    time counts against the provider/no-new-dispatch deadline, not a hard native
    or total-HTTP completion promise. Observer receives safe snapshots, never
    credentials, response reasoning or arbitrary exception text.
    """
    started = time.monotonic() if request_started_at is None else request_started_at
    deadline = started + PROVIDER_DEADLINE_SECONDS
    expected_day = expected_day or utc_day()
    parent_id = request_id or uuid.uuid4().hex
    original = deepcopy(prepared)
    trace = initial_pipeline_trace(parent_id, expected_day)
    disconnect_seen = asyncio.Event()
    disconnect_reason = 'client_disconnected'
    current = None
    frozen_baseline_utf8 = None

    def notify():
        trace['elapsed_seconds'] = max(0, time.monotonic() - started)
        if observer is not None:
            observer(deepcopy(trace))

    def fail(code, status_code=None):
        return PipelineFailure(code, deepcopy(trace), status_code)

    async def available():
        if disconnect_seen.is_set():
            raise fail(disconnect_reason)
        if disconnected is not None:
            try:
                gone = await disconnected()
            except asyncio.CancelledError:
                raise
            except Exception:
                raise fail('disconnect_check_failed') from None
            if gone:
                disconnect_seen.set()
                raise fail('client_disconnected')
        if time.monotonic() >= deadline:
            raise fail('provider_deadline')
        if utc_day() != expected_day:
            raise fail('utc_day_changed')

    async def run_stage(client, stage, body, input_bound, normalize):
        nonlocal current
        current = stage
        stage.update(state='prepared', prepared_elapsed_seconds=time.monotonic()-started,
                     prepared_request_sha256=digest(body),
                     reserved_input_tokens=input_bound + INPUT_ALLOWANCE,
                     reserved_output_tokens=config.max_output_tokens)
        notify()
        await available()
        cost = config.maximum_cost_microusd(input_bound)
        receipt = limits.reserve_stage(cost, expected_day, parent_id, stage['phase'])
        stage['reservation_receipt'] = deepcopy(receipt)
        if receipt.get('reserved') is not True:
            stage['state'] = 'failed'
            stage['failure_code'] = 'reservation_refused'
            notify()
            raise fail('reservation_refused')
        stage.update(state='reserved', reservation_microusd=cost,
                     reserved_elapsed_seconds=time.monotonic()-started)
        notify()
        await available()

        async def phase_available():
            await available()
            if time.monotonic() >= phase_deadline:
                raise fail('provider_stage_timeout')

        async def on_request(actual):
            first_hook=stage['state']=='reserved' and stage['provider_attempts']==0
            try:
                await phase_available()
                if not first_hook or str(actual.url)!='https://api.anthropic.com/v1/messages':
                    raise fail('duplicate_or_unreserved_dispatch')
                capture, actual_body = outgoing_request_capture(actual, phase_context={
                    'pipeline_version': PIPELINE_VERSION, 'effort_policy': EFFORT_POLICY,
                    'base_config_effort': config.effort, 'phase': stage['phase']})
                stage['outgoing_request'] = capture
                if (actual_body is None or actual_body != body
                        or digest(actual_body)!=stage['prepared_request_sha256']):
                    raise fail('request_capture_mismatch')
                check_phase_request(actual_body, pipeline_version=PIPELINE_VERSION,
                                    effort_policy=EFFORT_POLICY, base_config_effort=config.effort, phase=stage['phase'])
                proof=verify_wire_binding(capture['body_utf8'],json.loads(frozen_baseline_utf8),
                    stage['span_registry_sha256'],phase=stage['phase'],
                    draft_body_utf8=(trace['phases'][0]['outgoing_request']['body_utf8']
                                     if stage['phase']=='reconstruction' else None))
                stage['source_equality'].update(proof)
                stage.update(state='dispatched', provider_attempts=1, dispatch_status='initiated_receipt_unconfirmed',
                         dispatched_elapsed_seconds=time.monotonic() - started,
                         request_shape={'model':body['model'], 'version':API_VERSION,
                            'max_tokens':body['max_tokens'], 'service_tier':body['service_tier'],
                            'effort':body['output_config']['effort'], 'thinking':body['thinking']['type'],
                            'format':body['output_config']['format']['type']})
                # No transport has started; even persistence can cross a deadline.
                notify()
                await phase_available()
            except BaseException:
                if first_hook:stage.update(provider_attempts=0, dispatch_status='blocked_before_transport')
                raise

        def on_response(metadata, payload=None):
            stage.update(deepcopy(metadata))
            stage['dispatch_status'] = 'http_response_received'
            if payload is not None:
                stage['final_output_diagnostic'] = final_json_capture(payload, phase=stage['phase'],
                    anchor_protocol=ANCHOR_PROTOCOL, paragraph_protocol=PARAGRAPH_PROTOCOL,
                    answer_style=original.answer_style,plan_protocol=PLAN_PROTOCOL,
                    final_internal_protocol=FINAL_INTERNAL_PROTOCOL)
            notify()

        phase_started = time.monotonic()
        phase_deadline = min(deadline, phase_started + PROVIDER_STAGE_SECONDS)
        try:
            async with asyncio.timeout(max(0, phase_deadline - phase_started)):
                content = await client.send(body, on_request=on_request, on_response=on_response,
                                            paragraph_protocol=PARAGRAPH_PROTOCOL,
                                            answer_style=original.answer_style, phase=stage['phase'],
                                            pipeline_version=PIPELINE_VERSION, effort_policy=EFFORT_POLICY,
                                            base_config_effort=config.effort,plan_protocol=PLAN_PROTOCOL,
                                            final_internal_protocol=FINAL_INTERNAL_PROTOCOL)
        except TimeoutError:
            raise fail('provider_deadline' if time.monotonic() >= deadline else 'provider_stage_timeout') from None
        except (AnswerEnvelopeError, PhasePolicyError):
            if stage['provider_attempts'] == 0:
                stage['dispatch_status'] = 'blocked_before_transport'
            raise
        await available()
        if time.monotonic() >= phase_deadline:
            # A misbehaving transport can suppress task cancellation and return
            # late. It must not turn an expired stage into a successful final.
            raise fail('provider_stage_timeout')
        if stage['provider_attempts'] != 1 or stage.get('provider_http_status') != 200:
            raise fail('missing_dispatch_or_response')
        stage['usage_within_reservation'] = usage_within_bound(stage)
        if not stage['usage_within_reservation']:
            raise fail('usage_unverified')
        result = normalize(content)
        await available()
        stage.update(state='completed', mechanical_passed=True,
                     phase_seconds=time.monotonic() - phase_started,
                     completed_elapsed_seconds=time.monotonic() - started)
        notify()
        return result

    async def execute():
        nonlocal current, frozen_baseline_utf8
        try:
            try:
                validate_pipeline_config(config)
            except PhasePolicyError:
                raise fail('pipeline_configuration')
            await available()
            trace['status'] = 'prepared'
            trace['pair_preflight'] = limits.preflight_pair(pair_maximum_costs(config), expected_day)
            notify()
            if not trace['pair_preflight'].get('allowed'):
                raise fail('pair_allowance_refused')
            await available()
            # Preserve the legacy preparation/selection exactly. The new wire
            # prompt is applied only after it has selected the complete input.
            original_body = message_request(config, original)
            selected_draft = prepare_span_draft(request,original)
            draft_body = span_draft_message_request(config,selected_draft)
            frozen_baseline_utf8=encoded(selected_draft.baseline).decode()
            async with client_factory() as client:
                # The real transport checks its actual credential/workspace
                # values locally. No unchecked baseline reaches an observer,
                # reservation or HTTP dispatch, even if annotation splits it.
                safety,safe_baseline=client.capture_prepared_original(original_body,selected_draft.baseline)
                if safe_baseline is None or encoded(safe_baseline).decode()!=frozen_baseline_utf8:
                    raise fail('unsafe_prepared_original')
                trace['prepared_original']=deepcopy(safe_baseline)
                trace['prepared_original_safety']=deepcopy(safety)
                current=trace['phases'][0]
                current.update(source_equality={'complete_evidence_equal':True},
                    request_scope=deepcopy(safe_baseline['request_scope']),
                    input_binding_sha256=selected_draft.binding_sha256,anchor_protocol=ANCHOR_PROTOCOL,
                    span_registry_sha256=selected_draft.span_registry_sha256,
                    span_registry={key:{k:v for k,v in span.items() if k!='text'} for key,span in selected_draft.span_registry.items()},
                    annotated_payload_sha256=selected_draft.annotated_payload_sha256)
                def observe_resolution(value):
                    current['deterministic_support_resolution']=value
                    notify()
                draft = await run_stage(client,current,draft_body,selected_draft.input_token_bound,
                    lambda content:normalize_span_draft(content,selected_draft,resolved_observer=observe_resolution))
                trace['phases'][0]['validated_plan'] = deepcopy(draft)
                trace['phases'][0]['validated_plan_sha256'] = digest(draft)
                # Preparation cannot discard any source or retained history.
                current = trace['phases'][1]
                correction = prepare_reconstruction(request, original, draft)
                correction_body = reconstruction_message_request(config, correction)
                first_payload = json.loads(original.messages[-1]['content'])
                next_payload = json.loads(correction.messages[-1]['content'])
                preserved,actual_registry = verify_annotated_payload(
                    {k:next_payload[k] for k in ('question','sources','evidence')},first_payload)
                if preserved != first_payload or correction.messages[1:-1] != original.messages[1:-1]:
                    raise fail('evidence_identity_changed')
                current.update(compact_plan=deepcopy(correction.compact_plan),plan_sha256=digest(correction.compact_plan),
                    source_equality={'prepared_original_sha256':digest(first_payload), 'reconstruction_sha256':digest(preserved),
                                     'retained_history_equal':True, 'complete_evidence_equal':True},
                    request_scope=next_payload['request_scope'], input_binding_sha256=correction.binding_sha256,
                    anchor_protocol=ANCHOR_PROTOCOL,span_registry_sha256=correction.span_registry_sha256,
                    span_registry={key:{k:v for k,v in span.items() if k!='text'} for key,span in actual_registry.items()},
                    annotated_payload_sha256=correction.annotated_payload_sha256)
                final, assembly = await run_stage(client, current, correction_body, correction.input_token_bound,
                    lambda content: normalize_reconstruction(content, correction,resolved_observer=observe_resolution))
                trace['assembly_offsets'] = assembly
                await available()
            await available()
            trace.update(status='completed', final_answer=deepcopy(final))
            notify()
            return PipelineResult(final, deepcopy(trace))
        except asyncio.CancelledError:
            trace.pop('final_answer', None)
            trace.update(status='cancelled', failure_code=disconnect_reason if disconnect_seen.is_set() else 'request_cancelled')
            if current is not None and current['state'] != 'completed':
                current.update(state='cancelled', failure_code=trace['failure_code'])
            for stage in trace['phases']:
                if stage['state'] == 'not_started':stage['state'] = 'skipped'
            notify()
            raise
        except Exception as error:
            trace.pop('final_answer', None)
            code = error.code if isinstance(error, PipelineFailure) else (
                'provider_error' if isinstance(error, AnthropicAPIError) else 'local_validation_failure')
            trace.update(status='failed', failure_code=code)
            if current is not None and current['state'] != 'completed':
                current.update(state='failed', failure_code=code)
            for stage in trace['phases']:
                if stage['state'] == 'not_started':stage['state'] = 'skipped'
            notify()
            raise PipelineFailure(code, deepcopy(trace), getattr(error, 'status_code', None)) from None

    worker = asyncio.create_task(execute())
    async def watch_disconnect():
        nonlocal disconnect_reason
        while not worker.done():
            try:
                if await disconnected():
                    disconnect_seen.set()
                    worker.cancel()
                    return
            except asyncio.CancelledError:
                raise
            except Exception:
                disconnect_reason = 'disconnect_check_failed'
                disconnect_seen.set()
                worker.cancel()
                return
            await asyncio.sleep(0.025)
    watcher = asyncio.create_task(watch_disconnect()) if disconnected is not None else None
    try:
        return await worker
    except asyncio.CancelledError:
        if disconnect_seen.is_set():
            raise PipelineFailure(disconnect_reason, deepcopy(trace)) from None
        raise
    finally:
        if watcher is not None:
            watcher.cancel()
            try:await watcher
            except asyncio.CancelledError:pass
