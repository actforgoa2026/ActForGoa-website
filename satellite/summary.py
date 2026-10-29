"""Evidence-linked answers from checked measurements and fixed model choices.

No prose, counts, geometry or event dates are accepted from a language model.
"""
from datetime import datetime
from .domain import IST


def canopy_presence(evidence, classification):
    """Presence in a selected footprint is not identity tracking of one tree."""
    answers = classification.get('answers', {}) if classification.get('state') == 'complete' and evidence['state'] == 'observable' else {}
    before = answers.get('before_canopy', {}).get('choice', 'uncertain')
    after = answers.get('after_canopy', {}).get('choice', 'uncertain')
    if before not in {'yes', 'no'}: before = 'uncertain'
    if after not in {'yes', 'no'}: after = 'uncertain'
    outcomes = {
        ('yes', 'no'): ('possible_disappearance', 'Canopy was identified before and was not identified at the same location afterward. This suggests possible canopy loss; it does not establish cutting or loss of a particular tree.'),
        ('no', 'yes'): ('possible_appearance', 'Canopy was identified only in the later observation. Growth, seasonal visibility or image differences need review; this does not establish planting.'),
        ('yes', 'yes'): ('visible_both', 'Canopy was identified in both observations. This does not mean every tree remained: partial loss within the selected area can still occur.'),
        ('no', 'no'): ('not_identified', 'Canopy was not identified in either observation. This does not establish that no trees were present.'),
    }
    state, interpretation = outcomes.get((before, after), ('inconclusive', 'At least one presence decision is uncertain. A reliable presence-to-absence change cannot be inferred.'))
    if state == 'possible_disappearance' and answers.get('canopy_change', {}).get('choice') == 'no_visible_loss':
        state, interpretation = 'conflicting_evidence', 'The presence decisions suggest disappearance, but the change assessment reports no visible loss. The disagreement needs review.'
    return {'before': before, 'after': after, 'state': state, 'interpretation': interpretation,
            'scope': 'Same selected area and common usable pixels; not an individual-tree identification.'}


def summarize_comparison(intent, evidence, classification, interval):
    answers = classification.get('answers', {}) if classification.get('state') == 'complete' else {}
    choices = {name: answer.get('choice', 'uncertain') for name, answer in answers.items()}
    patches = evidence['candidates']['features']
    count = len(patches)
    coverage = evidence['common_usable_fraction']
    relation = interval.get('query_window_relation')
    statements = []

    def add(text, *sources):
        statements.append({'text': text, 'sources': list(sources)})

    def observed(instant):
        return datetime.fromisoformat(instant.replace('Z', '+00:00')).astimezone(IST).strftime('%d %b %Y, %H:%M IST')

    add(f"The selected observations were acquired on {observed(interval['before'])} and {observed(interval['after'])}.", 'before', 'after')
    add(f'{coverage:.1%} of the selected area is usable in both observations under the current cloud and shadow mask.', 'coverage')
    state = 'inconclusive'
    if evidence['state'] != 'observable':
        headline = 'There is not enough clear imagery to assess this area reliably.'
        add('Cloud, shadow or missing data prevents a reliable comparison across the selected area. An unobserved area is not evidence of no change.', 'coverage')
    elif intent == 'canopy_loss':
        presence = canopy_presence(evidence, classification)
        add(presence['interpretation'], 'assessment', 'before', 'after')
        change = choices.get('canopy_change', 'uncertain')
        if count:
            area = sum(f['properties']['area_m2'] for f in patches)
            qualifier = 'At least ' if evidence.get('candidates_truncated') else ''
            add(f'{qualifier}{count} possible vegetation-loss patch'+('es' if count != 1 else '')+
                f' met the exploratory thresholds; the reported patches cover {area:,.0f} m². These are not tree counts.', 'spectral')
            headline, state = 'Possible vegetation loss needs a closer look.', 'review_required'
        else:
            add('No vegetation-loss patches met the current reflectance and minimum-size thresholds. This does not rule out smaller changes or tree removal.', 'spectral')
            headline, state = 'The numeric check found no qualifying vegetation-loss patches.', 'no_candidate_detected'
        if change == 'possible_loss':
            add('The image assessment suggests possible canopy loss. Its interpretation needs review and does not establish cutting.', 'assessment')
            headline, state = 'Possible canopy loss needs review alongside the images.', 'review_required'
            if not count or choices.get('before_canopy') == 'no':
                headline, state = 'The checks do not agree about possible canopy loss.', 'conflicting_evidence'
                add('The image assessment and other checks do not give consistent support for canopy loss. Review both observations before drawing a conclusion.', 'spectral', 'assessment')
        elif change == 'no_visible_loss':
            add('The image assessment did not identify visible canopy loss. That is not proof that no trees were removed.', 'assessment')
            if count:
                headline, state = 'The numeric and visual checks do not agree.', 'conflicting_evidence'
        else:
            add('The image assessment could not establish whether canopy was lost.' if answers else 'No image assessment is available; the result above is a numeric vegetation check.', 'assessment')
        if presence['state'] == 'possible_disappearance':
            headline, state = 'The presence decisions suggest possible canopy loss.', 'review_required'
            if not count:
                headline, state = 'The presence decisions and numeric check need review together.', 'conflicting_evidence'
        elif presence['state'] == 'conflicting_evidence':
            headline, state = 'The image decisions do not agree about canopy loss.', 'conflicting_evidence'
    else:
        key = {'fire': 'fire_evidence', 'surface_water': 'surface_water', 'land_change': 'land_change', 'waste':'waste_evidence'}[intent]
        descriptions = {
            'possible_burn': 'The image assessment suggests a possible burn-like change.',
            'no_visible_burn': 'The image assessment did not identify a visible burn scar.',
            'visible_water': 'The image assessment suggests visible surface water in the later observation.',
            'no_visible_water': 'The image assessment did not identify surface water in the later observation.',
            'possible_clearing': 'The image assessment suggests possible new bare ground or clearing.',
            'possible_construction': 'The image assessment suggests possible new built surfaces.',
            'no_visible_change': 'The image assessment did not identify a substantial land-surface change.',
            'possible_large_accumulation':'The image assessment suggests a possible large accumulation of material that needs closer inspection.',
            'no_resolvable_accumulation':'The image assessment did not resolve a large accumulation of material.',
        }
        choice = choices.get(key, 'uncertain')
        headline = descriptions.get(choice, 'The available evidence does not resolve this question.')
        state = 'review_required' if choice in descriptions else 'inconclusive'
        add(headline+' The assessment remains unvalidated and may miss small or obscured features.', 'assessment', 'before', 'after')
        if intent == 'fire':
            add('FIRMS fire detections have not been queried. These images cannot establish that no fire occurred.', 'assessment')
        if intent == 'waste':
            add('Ordinary litter, small dumps and the type of material cannot be reliably identified at this resolution. Field reports or finer imagery are needed to establish dumping.', 'before', 'after')
        if intent == 'land_change':
            add('Visible development does not establish whether construction is lawful. Parcel permissions and applicable planning records have not been checked.', 'before', 'after')
        water=evidence.get('water_change')
        if intent == 'surface_water' and water:
            add(f"On the common usable area, the scene classification labels {water['before_area_m2']:,.0f} m² as water before and {water['after_area_m2']:,.0f} m² afterward; {water['gained_area_m2']:,.0f} m² gained and {water['lost_area_m2']:,.0f} m² lost that label.", 'spectral')
            add('Tides, seasonality, sediment and classification errors can affect these boundaries. This does not measure flow, depth or water quality.', 'spectral', 'before', 'after')
            if water['gained_area_m2']+water['lost_area_m2']>=900:
                headline,state='Water-classified cover changed between these observations.','review_required'
    if relation == 'overlaps_window':
        add('The image interval overlaps your requested period. A possible change may have started before that period.', 'before', 'after')
    elif relation == 'outside_window':
        headline, state = 'These observations do not cover your requested period.', 'outside_window'
        add('This pair cannot answer what changed within your requested period. Choose observations closer to that period.', 'before', 'after')
    elif relation == 'within_window':
        add('Both observations fall within your requested period; an exact event date still cannot be determined.', 'before', 'after')
    add('These observations do not establish an individual-tree count, a cause of change, or an exact event date. Findings need local review.', 'before', 'after')
    return {'state': state, 'headline': headline, 'statements': statements, 'method': 'checked-evidence-v1'}
