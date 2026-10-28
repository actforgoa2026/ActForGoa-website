import json
from pathlib import Path
import subprocess
import sys

import pytest
from scripts import evaluate_research_copy as evaluation


@pytest.fixture
def preservation_source(tmp_path):
    source = tmp_path/'preserved'
    (source/'.research-index').mkdir(parents=True)
    (source/'corpus/raw').mkdir(parents=True)
    (source/'.research-index/CURRENT.json').write_text('{"generation":"fixture"}')
    (source/'corpus/raw/public.txt').write_text('public source')
    return source


def test_child_failure_and_close_write_stay_on_copy(preservation_source, tmp_path, monkeypatch):
    output = tmp_path/'report.json'
    before = evaluation.inventory(preservation_source)
    real_run = subprocess.run

    def child(command, **kwargs):
        if command[0] == 'cp':
            return real_run(command, **kwargs)
        scratch = Path(command[command.index('--data-root')+1])
        assert scratch != preservation_source
        # Model a native close-time write followed by a failing evidence gate.
        (scratch/'.research-index/CURRENT.json').write_text('native close metadata')
        return subprocess.CompletedProcess(command, 1)

    monkeypatch.setattr(evaluation.subprocess, 'run', child)
    monkeypatch.setattr(sys, 'argv', ['evaluate', '--data-root', str(preservation_source),
                                    '--cases', str(tmp_path/'cases.json'), '--output', str(output)])
    assert evaluation.main() == 1
    assert evaluation.inventory(preservation_source) == before
    report = json.loads(output.with_suffix('.preservation.json').read_text())
    assert report['source_unchanged_after_child_exit']
    assert report['working_copy_changed_files'] == ['.research-index/CURRENT.json']


def test_source_change_is_detected_after_child_exit(preservation_source, tmp_path, monkeypatch):
    output = tmp_path/'report.json'
    real_run = subprocess.run

    def child(command, **kwargs):
        if command[0] == 'cp':
            return real_run(command, **kwargs)
        # Simulate an unexpected concurrent writer to the synthetic source.
        (preservation_source/'.research-index/CURRENT.json').write_text('unexpected change')
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(evaluation.subprocess, 'run', child)
    monkeypatch.setattr(sys, 'argv', ['evaluate', '--data-root', str(preservation_source),
                                    '--cases', str(tmp_path/'cases.json'), '--output', str(output)])
    with pytest.raises(RuntimeError, match='Preservation source changed'):
        evaluation.main()
    assert not json.loads(output.with_suffix('.preservation.json').read_text())['source_unchanged_after_child_exit']


def test_reports_cannot_be_written_inside_preserved_source(preservation_source, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['evaluate', '--data-root', str(preservation_source),
                                    '--cases', '/unused.json', '--output', str(preservation_source/'report.json')])
    with pytest.raises(SystemExit) as error:
        evaluation.main()
    assert error.value.code == 2
    assert not (preservation_source/'report.json').exists()


def test_preservation_inventory_rejects_symlinks(preservation_source):
    (preservation_source/'corpus/raw/alias').symlink_to(preservation_source/'corpus/raw/public.txt')
    with pytest.raises(ValueError, match='symlinks'):
        evaluation.inventory(preservation_source)


@pytest.mark.parametrize('marker', ['snapshot-files.json', 'seal.json'])
def test_copy_reports_cannot_modify_another_preservation_directory(preservation_source, tmp_path, monkeypatch, marker):
    protected = tmp_path/'sealed-package'
    protected.mkdir()
    (protected/marker).write_text('{}')
    output = protected/'reports/evaluation.json'
    monkeypatch.setattr(sys, 'argv', ['evaluate', '--data-root', str(preservation_source),
                                    '--cases', '/unused.json', '--output', str(output)])
    with pytest.raises(SystemExit) as error:
        evaluation.main()
    assert error.value.code == 2
    assert not output.parent.exists()


@pytest.mark.parametrize('marker', ['snapshot-files.json', 'seal.json'])
def test_direct_gate_rejects_preservation_before_opening_native_index(preservation_source, tmp_path, monkeypatch, marker):
    from scripts import evaluate_retrieval_evidence as direct
    (preservation_source/marker).write_text('{}')

    def forbidden_open(*args, **kwargs):
        raise AssertionError('Native index must never open a preservation source')

    monkeypatch.setattr(direct, 'Library', forbidden_open)
    monkeypatch.setattr(sys, 'argv', ['evaluate', '--data-root', str(preservation_source),
                                    '--cases', '/unused.json', '--output', str(tmp_path/'result.json')])
    with pytest.raises(SystemExit) as error:
        direct.main()
    assert error.value.code == 2
