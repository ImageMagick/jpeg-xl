#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Tools"))

from dependency_updater import Step, Updater

URL = "https://github.com/libjxl/libjxl/archive/refs/tags/v{version}.tar.gz"

GENERATED_HEADERS = (
    "jxl_cms_export.h",
    "jxl_export.h",
    "jxl_threads_export.h",
    "version.h",
)


def update_source(updater):
    updater.replace_source()
    updater.remove(".github")
    updater.update_config()


def create_headers(updater):
    dependencies = updater.dependency_dir.parent
    highway = dependencies / "highway"
    brotli = dependencies / "brotli"
    lcms = dependencies / "lcms"
    updater.cmake(
        "-DBUILD_SHARED_LIBS=ON",
        "-DBUILD_TESTING=OFF",
        "-DJPEGXL_ENABLE_TOOLS=OFF",
        "-DJPEGXL_ENABLE_DOXYGEN=OFF",
        "-DJPEGXL_ENABLE_MANPAGES=OFF",
        "-DJPEGXL_ENABLE_EXAMPLES=OFF",
        "-DJPEGXL_ENABLE_BENCHMARK=OFF",
        "-DJPEGXL_ENABLE_FUZZERS=OFF",
        "-DJPEGXL_ENABLE_JNI=OFF",
        "-DJPEGXL_ENABLE_JPEGLI=OFF",
        "-DJPEGXL_ENABLE_SKCMS=OFF",
        "-DJPEGXL_FORCE_SYSTEM_LCMS2=ON",
        "-DJPEGXL_BUNDLE_LIBPNG=OFF",
        "-DJPEGXL_ENABLE_SJPEG=OFF",
        f"-DHWY_INCLUDE_DIR:PATH={highway.as_posix()}",
        f"-DHWY_LIBRARY:FILEPATH={(highway / 'foo.lib').as_posix()}",
        f"-DBROTLI_INCLUDE_DIR:PATH={(brotli / 'c/include').as_posix()}",
        f"-DBROTLICOMMON_LIBRARY:FILEPATH={(brotli / 'foo.lib').as_posix()}",
        f"-DBROTLIENC_LIBRARY:FILEPATH={(brotli / 'foo.lib').as_posix()}",
        f"-DBROTLIDEC_LIBRARY:FILEPATH={(brotli / 'foo.lib').as_posix()}",
        f"-DLCMS2_INCLUDE_DIR:PATH={(lcms / 'include').as_posix()}",
        f"-DLCMS2_LIBRARY:FILEPATH={(lcms / 'foo.lib').as_posix()}")
    updater.copy_from_build("lib/include/jxl", GENERATED_HEADERS, "lib/include/jxl")
    updater.remove_build()


def disable_wasm_threads(updater):
    updater.apply_patches()


updater = Updater(__file__, "libjxl", URL)
updater.run([
    Step("Replace the source with the release and update Config.txt", update_source,
        "Updated jpeg-xl to {version}"),
    Step("Generate the header files with cmake", create_headers,
        "Added files that were created with cmake."),
    Step("Disable threading for wasm", disable_wasm_threads,
        "Disable threading for wasm build."),
    updater.clone_dependencies_step(),
])
