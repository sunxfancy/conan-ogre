from conans import ConanFile, CMake
from conans.tools import download, unzip, SystemPackageTool
import os

class OgreConan(ConanFile):
    name = "OGRE"
    version = "1.10.11.0"
    description = "Open Source 3D Graphics Engine"
    folder = 'ogre-1.10.11'
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    exports = '*'
    options = {
        "shared": [True, False],
        "use_cpp11": [True, False],
        "with_boost": [True, False],
        "with_poco": [True, False],
        "with_cg": [True, False]
    }
    default_options = (
        "shared=True",
        "use_cpp11=True",
        "with_boost=False",
        "with_poco=False",
        "with_cg=True"
    )
    
    url = "http://github.com/sunxfancy/conan-ogre"
    license = 'MIT'
    folderName = 'ogre-1.10.11'

    def configure(self):
        if 'x86' not in str(self.settings.arch):
            self.options.with_cg = False

    def system_requirements(self):
        if self.settings.os == 'Linux':
            installer = SystemPackageTool()
            if self.settings.arch == 'x86':
                installer.install("libxmu-dev:i386")
                installer.install("libxaw7-dev:i386")
                installer.install("libxt-dev:i386")
                installer.install("libxrandr-dev:i386")
            elif self.settings.arch == 'x86_64':
                installer.install("libxmu-dev:amd64")
                installer.install("libxaw7-dev:amd64")
                installer.install("libxt-dev:amd64")
                installer.install("libxrandr-dev:amd64")

    def extractFromUrl(self, url):
        self.output.info('download {}'.format(url))
        filename = os.path.basename(url)
        if not os.path.isfile(os.path.join(self.source_folder, filename)):
            print(os.path.join(self.source_folder, filename))
            download(url, filename)
        unzip(filename)
        # os.unlink(filename)

    def source(self):
        self.extractFromUrl("https://github.com/OGRECave/ogre/archive/v1.10.11.zip")

    def build(self):
        cmake = CMake(self)
        srcDir = os.path.join(self.source_folder, self.folderName)
        self.installDir = os.path.join(self.source_folder, 'install')
        options = {
            'OGRE_BUILD_TESTS': False,
            'OGRE_BUILD_TOOLS': False,
            'OGRE_INSTALL_PDB': False,
            'OGRE_USE_BOOST': self.options.with_boost,
            'CMAKE_INSTALL_PREFIX:': self.installDir
        }
        if not os.path.exists('build'):
            os.mkdir('build')
        cmake.configure(source_folder=srcDir, build_folder='build')
        cmake.build(target='install')

    def package(self):
        sdk_dir = self.installDir
        include_dir = os.path.join(sdk_dir, 'include', 'OGRE')
        lib_dir = os.path.join(sdk_dir, 'lib')
        bin_dir = os.path.join(sdk_dir, 'bin')
        self.copy(pattern="*.h", dst="include/OGRE", src=include_dir)
        self.copy("*.lib", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.a", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.so*", dst="lib", src=lib_dir, keep_path=False, links=True)
        self.copy("*.dylib", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.dll", dst="bin", src=bin_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = [
            'OgreMain',
            'OgreOverlay',
            'OgrePaging',
            'OgreProperty',
            'OgreRTShaderSystem',
            'OgreTerrain'
        ]

        is_apple = (self.settings.os == 'Macos' or self.settings.os == 'iOS')
        if self.settings.build_type == "Debug" and not is_apple:
            self.cpp_info.libs = [lib+'_d' for lib in self.cpp_info.libs]

        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('rt')
