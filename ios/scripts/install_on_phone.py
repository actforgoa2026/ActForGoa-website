#!/usr/bin/env python3
"""Install a signed development app over USB without opening Device Hub or Xcode."""
import argparse
import plistlib
import shutil
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--app', type=Path, default=Path(__file__).resolve().parents[1] / 'device-build/Build/Products/Debug-iphoneos/ActForGoa.app')
args = parser.parse_args()
app = args.app.resolve()
installer = shutil.which('ideviceinstaller')
identifier = shutil.which('idevice_id')
if not installer or not identifier:
    raise SystemExit('Install the USB tools with: brew install ideviceinstaller libimobiledevice')
if not app.is_dir():
    raise SystemExit('Build the signed iPhone app first. See ios/README.md.')
subprocess.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', str(app)], check=True)
profile = plistlib.loads(subprocess.check_output(['/usr/bin/security', 'cms', '-D', '-i', str(app / 'embedded.mobileprovision')]))
if not profile['Entitlements'].get('get-task-allow'):
    raise SystemExit('This is not a development provisioning profile.')
info = plistlib.loads((app / 'Info.plist').read_bytes())
devices = subprocess.check_output([identifier, '-l'], text=True).splitlines()
if not devices:
    raise SystemExit('No USB iPhone is visible. Connect and unlock the phone, and trust this Mac if prompted.')
eligible = [device for device in devices if device in profile.get('ProvisionedDevices', [])]
if len(eligible) != 1:
    raise SystemExit('Expected exactly one connected phone included in this provisioning profile. Select the intended phone and rebuild its development profile if needed.')
phone = eligible[0]
subprocess.run([installer, '-u', phone, 'install', str(app)], check=True)
installed = plistlib.loads(subprocess.check_output([installer, '-u', phone, 'list', '-b', info['CFBundleIdentifier'], '--xml']))
record = next((r for r in installed if r.get('CFBundleIdentifier') == info['CFBundleIdentifier']), None)
if not record or record.get('CFBundleVersion') != info['CFBundleVersion']:
    raise SystemExit('The installation command finished, but the installed version could not be verified.')
print(f"Verified installation: {info['CFBundleDisplayName']} {info['CFBundleShortVersionString']} ({info['CFBundleVersion']}). Open it on the phone to verify physical behavior.")
