"""Offline review commands must reject preservation paths before native imports."""
from pathlib import Path
import subprocess
import sys

import pytest

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/'reports/passage-selection-2026-10-27'


@pytest.mark.parametrize('entry',['evaluate.py','capture_sources.py','capture_assessment_sources.py'])
def test_review_children_reject_preservation_markers_through_symlink(tmp_path,entry):
    preserved=tmp_path/'preserved';preserved.mkdir();(preserved/'seal.json').write_text('{}')
    data=preserved/'data';data.mkdir()
    alias=tmp_path/'alias';alias.symlink_to(data,target_is_directory=True)
    result=subprocess.run([sys.executable,str(REPORT/entry),'--data-root',str(alias),
                           '--output',str(tmp_path/'out.json')],capture_output=True,text=True)
    assert result.returncode==2
    assert 'disposable-copy wrapper' in result.stderr.lower()
    assert not (tmp_path/'out.json').exists()


def test_review_child_rejects_unsealed_recovery_location(tmp_path):
    recovery=Path.home()/'Documents/ActForGoa Recovery/never-open-this'
    result=subprocess.run([sys.executable,str(REPORT/'evaluate.py'),'--data-root',str(recovery),
                           '--output',str(tmp_path/'out.json')],capture_output=True,text=True)
    assert result.returncode==2
    assert 'disposable-copy wrapper' in result.stderr.lower()
