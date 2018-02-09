from conans import ConanFile, CMake
from conans.tools import download, unzip, SystemPackageTool
import os

class OgreConan(ConanFile):
    name = "OGRE"
    version = "1.10.11"
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
        "with_cg": [True, False],
        "with_jni": [True, False],
        "with_python": [True, False],
        "build_samples": [True, False],
        "node_legacy": ['Map', 'Vector']
    }
    default_options = (
        "shared=True",
        "use_cpp11=False",
        "with_boost=False",
        "with_poco=False",
        "with_cg=False",
        "with_jni=False",
        "with_python=False",
        "build_samples=False",
        "node_legacy=Vector"
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
                installer.install("libgles2-mesa-dev:i386 libxmu-dev:i386 libxaw7-dev:i386 libxt-dev:i386 libxrandr-dev:i386 libsdl2-dev:i386")
            elif self.settings.arch == 'x86_64':
                installer.install("libgles2-mesa-dev:amd64 libxmu-dev:amd64 libxaw7-dev:amd64 libxt-dev:amd64 libxrandr-dev:amd64 libsdl2-dev:amd64")

    def extractFromUrl(self, url):
        self.output.info('download {}'.format(url))
        filename = os.path.basename(url)
        if not os.path.isfile(os.path.join(self.source_folder, filename)):
            download(url, filename)
        unzip(filename)
        # os.unlink(filename)

    def source(self):
        self.extractFromUrl("https://github.com/OGRECave/ogre/archive/v1.10.11.zip")

    def build(self):
        cmake = CMake(self)
        srcDir = os.path.join(self.source_folder, self.folderName)
        options = {
            'OGRE_BUILD_TESTS': False,
            'OGRE_BUILD_TOOLS': True,
            'OGRE_INSTALL_PDB': False,
            'OGRE_BUILD_LIBS_AS_FRAMEWORKS': False,
            'OGRE_BUILD_SAMPLES': self.options.build_samples,
            'OGRE_USE_STD11': self.options.use_cpp11,
            'OGRE_STATIC': not self.options.shared,
            'OGRE_BUILD_PLUGIN_CG': self.options.with_cg,
            'OGRE_BUILD_COMPONENT_PYTHON': self.options.with_python,
            'OGRE_BUILD_COMPONENT_JAVA': self.options.with_jni,
            'OGRE_NODE_STORAGE_LEGACY': (self.options.node_legacy == "Map")
        }
        if not os.path.exists('build'):
            os.mkdir('build')
        cmake.configure(defs=options, source_folder=srcDir, build_folder='build')
        cmake.build()
        cmake.install()

    def package(self):
        dependency_dir = os.path.join(self.build_folder, 'build', 'Dependencies')
        include_dir = os.path.join(dependency_dir, 'include')
        lib_dir = os.path.join(dependency_dir, 'lib')
        bin_dir = os.path.join(dependency_dir, 'bin')
        self.copy(pattern="*.h", dst="include/Dependencies", src=include_dir)
        self.copy("*.lib", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.dll", dst="bin", src=lib_dir, keep_path=False)
        self.copy("*.so*", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.dylib", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.a", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.dll", dst="bin", src=bin_dir, keep_path=False)

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = [
                'OgreMain',
                'OgreOverlay',
                'OgrePaging',
                'OgreProperty',
                'OgreRTShaderSystem',
                'OgreTerrain',
                'freetype',
                'zzip'
            ]
        else:
            self.cpp_info.libs = [
                'OgreMainStatic',
                'OgreOverlayStatic',
                'OgrePagingStatic',
                'OgrePropertyStatic',
                'OgreRTShaderSystemStatic',
                'OgreTerrainStatic',
                'freetype',
                'zzip'
            ]
        if self.settings.build_type == "Debug":
            self.cpp_info.libs = [lib + '_d' for lib in self.cpp_info.libs]
        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('rt')

        if self.settings.os == 'Macos':
            self.cpp_info.libs.append("z")
            self.cpp_info.exelinkflags.append("-framework Cocoa")
            self.cpp_info.exelinkflags.append("-framework Foundation")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
