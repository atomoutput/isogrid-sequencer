[app]

# (str) Title of your application
title = Isogrid Sequencer

# (str) Package name
package.name = isogrid

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin

# (list) List of exclusions using pattern matching
# Do not prefix with './'
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3, kivy, pyjnius

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (string) Full name of the ID of the Android app package
android.package.id = org.example.isogridsequencer

# (string) Android application genre
android.genre = Audio

# (list) Android permissions required
android.permissions = MIDI

# (int) Android API to use
android.api = 33

# (int) Minimum API required
android.minapi = 24

# (str) Android SDK directory (if empty, it will be automatically downloaded)
#android.sdk_path = 

# (str) Android NDK directory (if empty, it will be automatically downloaded)
#android.ndk_path = 

# (str) Android NDK stacktrace filename (if empty, no stacktrace)
#android.ndk_stacktrace_filename = 

# (str) Local rules to follow (instead of *rules.mk)
#android.local_rules = 

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy Android bundle to match the 32/64bit selected at build
android.copy_libs = 1

# (str) Android entry point, default is ok
#android.entry = org.renpy.android.PythonActivity

# (str) Android tag to assign to the asset (e.g. for debug/release)
#android.tag = prod

# (str) Android assets to use (comma separated strings)
#android.assets = 

# (str) Android java source (if empty, no java code is compiled)
#android.java_dir = 

# (str) Android package name to use
#android.package = org.example.isogridsequencer

# (str) Android activity name to use
#android.activity_class_name = org.renpy.android.PythonActivity

# (str) Python for android project directory
#p4a.project_dir = 

# (str) Android NDK version to use
#android.ndk_version = 23b

# (int) Override log level (0-2)
#android.log_level = 1

# (str) Android archs to build for (comma separated)
#android.archs = armeabi-v7a, arm64-v8a, x86_64

# (bool) Enable Androidx (indicate if you want to enable Androidx or not)
#android.enable_androidx = True

# (str) Path to a custom ndk packagename
# android.ndk_package = 

# (str) Java compile version
# android.java_compile_sdk = 

# (str) Local Maven repository
# android.maven_repository = 

# (str) Folder containing the presplash background
# android.presplash_bg = 

# (bool) Enable gradle (indicate if you want to enable gradle or not)
# android.gradle_enabled = True

# (str) Android gradle build directory (if empty, it will be automatically created)
# android.gradle_build_dir = 

# (list) Android extra jars
# android.extra_jars = 

# (str) Android additional Gradle dependencies
# android.gradle_dependencies = 

# (str) Android additional arguments to the Gradle build
# android.gradle_repositories = 

# (bool) Set to True if you want to run the application for the first time
# android.install_only_target = False

# (str) Additional arguments to setup.py file
# android.setup_py_args = 

# (str) Global command line arguments to be appended to the dist build
# buildozer.global_args = 

#
# iOS specific
#

# (str) Name of the certificate to use for signing the debug version
# get it from `buildozer ios list_identities`
#ios.codesign.debug = iPhone Developer: <lastname> <firstname> (<hexstring>)

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = iPhone Distribution: <lastname> <firstname> (<hexstring>)

# (str) Name of the provisioning profile to load for signing
#ios.p4a_attr.ios_app_id = <id>
#ios.provisioning_profile = 

# (str) The signing key to use
#ios.p4a_attr.keychain_password = <keychain password>

# (str) The password for the keychain signing certificate
#ios.keychain_certificate_password = <keychain certificate password>

# (bool) Bubblewrap Package
#ios.use_p4a_signer = False

# (str) Path to a custom p4a-specs repo [UNEXPERIMENTED]
#ios.p4a_repo = 

# (str) Specify a provided signature scheme
#ios.custom_signature_schemes = 

# (str) Provision profiles that override the automatic provisioning
#ios.manual_provisioning_descritpion = 

# (str) Path to a custom garden-to-p4a bridge recipe [UNEXPERIMENTED]
#ios.custom_masonry_recipe = 

# (str) Prohibited packages to pull in the kivy-ios-buildkit [UNEXPERIMENTED]
#ios.ios_buildkit_prohibited_packages = 

# (str) IP address of the host computer (workaround for macOS users)
#ios.ios_deploy_host_ip = 

# (str) iOS archive name
#ios.archive_name = 

# (str) Bundle version
#ios.bundle_version = 

# (bool) Use XCode 12 to build
#ios.use_xcode_12 = True


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display (0 = silent, 1 = target, 2 = everything)
display = 2