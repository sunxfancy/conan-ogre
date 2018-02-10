from conan.packager import ConanMultiPackager
from conans.tools import os_info
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="OGRE:shared", pure_c=False)
    # Disable VS2010 because of missing DirectX stuff

    # Keep only Release builds
    filtered_builds = []
    for settings, options, env_vars, build_requires, reference in builder.items:
        if settings["build_type"] == "Release" and settings["arch"] == "x86_64" and not (settings["compiler"] == "Visual Studio" and settings["compiler.version"] == "10"):
             filtered_builds.append([settings, options, env_vars, build_requires])
    builder.builds = filtered_builds

    builder.run()

