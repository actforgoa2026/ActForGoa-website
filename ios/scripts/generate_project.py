#!/usr/bin/env python3
"""Deterministic Xcode project generation, using Python's standard library only."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
objects = {}
def uid(name): return hashlib.sha1(name.encode()).hexdigest()[:24].upper()
def add(identifier, isa, **fields):
    key = uid(identifier); objects[key] = dict(isa=isa, **fields); return key
class Ref(str): pass
def ref(key): return Ref(key)
def render(v):
    if isinstance(v, Ref): return v
    if isinstance(v, dict): return '{ ' + ' '.join(f'{json.dumps(k)} = {render(value)};' for k, value in v.items()) + ' }'
    if isinstance(v, list): return '(' + ', '.join(render(x) for x in v) + (',' if v else '') + ')'
    return json.dumps(str(v))
def file(path, filetype): return add('file:'+path,'PBXFileReference',lastKnownFileType=filetype,path=path,sourceTree='<group>')
def build(path, f): return add('build:'+path, 'PBXBuildFile', fileRef=ref(f))
appfiles=[]; appbuild=[]
for p in sorted((ROOT/'ActForGoa').rglob('*.swift')):
    path=str(p.relative_to(ROOT)); f=file(path,'sourcecode.swift'); appfiles.append(ref(f)); appbuild.append(ref(build(path,f)))
content=file('ActForGoa/Content','folder'); appfiles.append(ref(content))
assets=file('ActForGoa/Assets.xcassets','folder.assetcatalog'); appfiles.append(ref(assets))
privacy=file('ActForGoa/PrivacyInfo.xcprivacy','text.xml'); appfiles.append(ref(privacy))
appProduct=add('product:app','PBXFileReference',explicitFileType='wrapper.application',path='ActForGoa.app',sourceTree='BUILT_PRODUCTS_DIR')
testProduct=add('product:test','PBXFileReference',explicitFileType='wrapper.cfbundle',path='ActForGoaUITests.xctest',sourceTree='BUILT_PRODUCTS_DIR')
products=add('products','PBXGroup',children=[ref(appProduct),ref(testProduct)],name='Products',sourceTree='<group>')
testfile=file('UITests/ActForGoaUITests.swift','sourcecode.swift')
group=add('root','PBXGroup',children=appfiles+[ref(testfile),ref(products)],sourceTree='<group>')
package=add('onnx','XCRemoteSwiftPackageReference',repositoryURL='https://github.com/microsoft/onnxruntime-swift-package-manager',requirement={'kind':'exactVersion','version':'1.24.2'})
dep=add('onnxproduct','XCSwiftPackageProductDependency',package=ref(package),productName='onnxruntime')
framework=add('onnxbuild','PBXBuildFile',productRef=ref(dep))
sync=add('sync','PBXShellScriptBuildPhase',buildActionMask=2147483647,files=[],inputPaths=[],outputPaths=[],alwaysOutOfDate=1,runOnlyForDeploymentPostprocessing=0,shellPath='/bin/sh',shellScript='/usr/bin/python3 "$SRCROOT/scripts/sync_resources.py"\n',name='Sync canonical web catalogue')
sources=add('sources','PBXSourcesBuildPhase',buildActionMask=2147483647,files=appbuild,runOnlyForDeploymentPostprocessing=0)
frameworks=add('frameworks','PBXFrameworksBuildPhase',buildActionMask=2147483647,files=[ref(framework)],runOnlyForDeploymentPostprocessing=0)
resources=add('resources','PBXResourcesBuildPhase',buildActionMask=2147483647,files=[ref(build('Content',content)),ref(build('Assets',assets)),ref(build('Privacy',privacy))],runOnlyForDeploymentPostprocessing=0)
testSources=add('testSources','PBXSourcesBuildPhase',buildActionMask=2147483647,files=[ref(build('test',testfile))],runOnlyForDeploymentPostprocessing=0)
common={'CLANG_ENABLE_MODULES':'YES','SWIFT_VERSION':'5.0','IPHONEOS_DEPLOYMENT_TARGET':'18.0','SDKROOT':'iphoneos','SUPPORTED_PLATFORMS':'iphoneos iphonesimulator','TARGETED_DEVICE_FAMILY':'1','ENABLE_USER_SCRIPT_SANDBOXING':'NO','CODE_SIGN_STYLE':'Automatic','SWIFT_EMIT_LOC_STRINGS':'YES','MARKETING_VERSION':'0.1.0','CURRENT_PROJECT_VERSION':'2','GENERATE_INFOPLIST_FILE':'NO'}
def configs(name, settings):
    ids=[]
    for config in ['Debug','Release']:
        s=dict(settings)
        if config=='Debug': s.update({'SWIFT_OPTIMIZATION_LEVEL':'-Onone','DEBUG_INFORMATION_FORMAT':'dwarf','ENABLE_TESTABILITY':'YES','SWIFT_ACTIVE_COMPILATION_CONDITIONS':'DEBUG','ONLY_ACTIVE_ARCH':'YES'})
        else: s.update({'SWIFT_OPTIMIZATION_LEVEL':'-O','DEBUG_INFORMATION_FORMAT':'dwarf-with-dsym'})
        ids.append(ref(add(name+config,'XCBuildConfiguration',buildSettings=s,name=config)))
    return add(name+'configs','XCConfigurationList',buildConfigurations=ids,defaultConfigurationIsVisible=0,defaultConfigurationName='Release')
projectConfig=configs('project',common)
appConfig=configs('app',{'PRODUCT_BUNDLE_IDENTIFIER':'org.actforgoa.fieldguide','PRODUCT_NAME':'$(TARGET_NAME)','INFOPLIST_FILE':'ActForGoa/Info.plist','ASSETCATALOG_COMPILER_APPICON_NAME':'AppIcon','LD_RUNPATH_SEARCH_PATHS':'$(inherited) @executable_path/Frameworks'})
testConfig=configs('tests',{'PRODUCT_BUNDLE_IDENTIFIER':'org.actforgoa.fieldguide.uitests','PRODUCT_NAME':'$(TARGET_NAME)','GENERATE_INFOPLIST_FILE':'YES','TEST_TARGET_NAME':'ActForGoa','CODE_SIGNING_ALLOWED':'NO'})
app=add('target:app','PBXNativeTarget',buildConfigurationList=ref(appConfig),buildPhases=[ref(sync),ref(sources),ref(frameworks),ref(resources)],buildRules=[],dependencies=[],name='ActForGoa',productName='ActForGoa',productReference=ref(appProduct),productType='com.apple.product-type.application',packageProductDependencies=[ref(dep)])
proxy=add('proxy','PBXContainerItemProxy',containerPortal=ref(uid('project')),proxyType=1,remoteGlobalIDString=app,remoteInfo='ActForGoa')
targetDep=add('testdep','PBXTargetDependency',target=ref(app),targetProxy=ref(proxy))
tests=add('target:tests','PBXNativeTarget',buildConfigurationList=ref(testConfig),buildPhases=[ref(testSources)],buildRules=[],dependencies=[ref(targetDep)],name='ActForGoaUITests',productName='ActForGoaUITests',productReference=ref(testProduct),productType='com.apple.product-type.bundle.ui-testing')
project=add('project','PBXProject',attributes={'LastUpgradeCheck':'1600','BuildIndependentTargetsInParallel':'YES','TargetAttributes':{app:{'CreatedOnToolsVersion':'16.0'},tests:{'CreatedOnToolsVersion':'16.0','TestTargetID':app}}},buildConfigurationList=ref(projectConfig),compatibilityVersion='Xcode 14.0',developmentRegion='en',hasScannedForEncodings=0,knownRegions=['en','Base'],mainGroup=ref(group),productRefGroup=ref(products),projectDirPath='',projectRoot='',targets=[ref(app),ref(tests)],packageReferences=[ref(package)])
text='// !$*UTF8*$!\n{\narchiveVersion = 1;\nclasses = {};\nobjectVersion = 60;\nobjects = {\n' + '\n'.join(f'{k} = {render(v)};' for k, v in objects.items()) + f'\n}};\nrootObject = {project};\n}}\n'
(ROOT/'ActForGoa.xcodeproj/project.pbxproj').write_text(text)
scheme=f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="1600" version="1.3">
<BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries><BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{app}" BuildableName="ActForGoa.app" BlueprintName="ActForGoa" ReferencedContainer="container:ActForGoa.xcodeproj"/></BuildActionEntry></BuildActionEntries></BuildAction>
<TestAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" shouldUseLaunchSchemeArgsEnv="YES"><Testables><TestableReference skipped="NO"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{tests}" BuildableName="ActForGoaUITests.xctest" BlueprintName="ActForGoaUITests" ReferencedContainer="container:ActForGoa.xcodeproj"/></TestableReference></Testables></TestAction>
<LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" debugServiceExtension="internal" allowLocationSimulation="YES"><BuildableProductRunnable runnableDebuggingMode="0"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{app}" BuildableName="ActForGoa.app" BlueprintName="ActForGoa" ReferencedContainer="container:ActForGoa.xcodeproj"/></BuildableProductRunnable></LaunchAction>
<ProfileAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES" savedToolIdentifier="" useCustomWorkingDirectory="NO" debugDocumentVersioning="YES"/>
<AnalyzeAction buildConfiguration="Debug"/><ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"/>
</Scheme>'''
(ROOT/'ActForGoa.xcodeproj/xcshareddata/xcschemes/ActForGoa.xcscheme').write_text(scheme)
print('Generated ActForGoa.xcodeproj')
