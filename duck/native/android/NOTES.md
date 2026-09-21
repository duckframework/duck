# Android SDK need to be installed

The build needs an Android SDK folder, but only a small part of it:

- `platforms/android-34/` (contains `android.jar`)
- `build-tools/<version>/`
- `licenses/` (accepted SDK licenses)

Point Gradle at it in `local.properties` (not committed to git):

```
sdk.dir=/path/to/android-sdk
```

or set `ANDROID_HOME`. Accept the licenses with `sdkmanager --licenses`.

## Termux / ARM64

Google's SDK ships x86_64 `aapt2`, which does not run on ARM64.

1. Download `android-sdk-aarch64-linux-android.tar.xz` from
   https://github.com/HomuHomu833/android-sdk-custom/releases
2. Extract it into Termux's home, not shared storage:

```
mkdir -p ~/android-sdk
tar -xf android-sdk-aarch64-linux-android.tar.xz -C ~/android-sdk
```

3. If it extracts into `~/android-sdk/android-sdk`, move the contents up
   one level.
4. Install Java and Termux's own `aapt2` (the one bundled in the custom SDK
   fails with `unexpected e_type`):

```
pkg install openjdk-17 aapt2 gradle
```

5. Set the override in `gradle.properties` (project root, not `app/`):

```
android.aapt2FromMavenOverride=/data/data/com.termux/files/usr/bin/aapt2
```

6. Create the license file so Gradle can download the platform:

```
mkdir -p ~/android-sdk/licenses
printf "\n24333f8a63b6825ea9c5514f83c2829b004d1fee\n" > ~/android-sdk/licenses/android-sdk-license
```

7. Generate the wrapper once, then build:

```
gradle wrapper
chmod +x gradlew
./gradlew assembleDebug
```

Keep the project inside `~/` (for example `~/duck-bridge`). Projects in
`/storage/emulated/0` cannot run `gradlew` (Permission denied).

# If aapt2 fails, try lowering compile SDK

Termux's `aapt2` is built from Android 13 tools and cannot read newer
`android.jar` files. The error looks like this:

```
AAPT: error: failed to load include path .../platforms/android-35/android.jar
```

Fix: lower `compileSdk` in `app/build.gradle.kts` (try 34, then 33):

```
compileSdk = 34
```

Leave `targetSdk` alone. Gradle downloads the matching platform on the next
build.

To test `aapt2` on its own against a platform:

```
aapt2 link -o test.apk -I ~/android-sdk/platforms/android-34/android.jar \
    --manifest AndroidManifest.xml
```

If `test.apk` is created, `aapt2` works with that platform.