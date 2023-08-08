#!/usr/bin/env python3


import argparse
import clang.cindex
import io
import sys
from functools import partial
from multiprocessing.pool import ThreadPool


if not sys.platform.startswith("win32"):
    from ctypes.util import find_library


def setup_clang(library):
    if library == None:
        # LibClang shared library default search paths
        if sys.platform.startswith("win32"):
            clang.cindex.Config.set_library_path("C:/Program Files/LLVM/bin")
        else:
            clang.cindex.Config.set_library_file(find_library('clang-10'))
            # clang.cindex.Config.set_library_path("/usr/lib")
    else:
        clang.cindex.Config.set_library_file(library)


def parse_any(cursor, className, classMembers, baseClassName):
    for children in cursor.get_children():
        try:
            if children.kind == clang.cindex.CursorKind.CLASS_DECL:
                parse_classdecl(children, className,
                                classMembers, baseClassName)
            else:
                parse_any(children, className, classMembers, baseClassName)
        except ValueError:
            pass


def parse_baseclasses(cursor, baseClassName):
    for children in cursor.get_children():
        try:
            if children.kind == clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
                base_class = children.get_definition()
                for base_children in base_class.get_children():
                    # print(base_children.displayname)
                    if base_children.displayname == "_cloneFrom(const Ogre::EmitterDefData * _Nonnull)":
                        baseClassName.append(base_class.spelling)
                        parse_baseclasses(base_class, baseClassName)
                        break
        except ValueError:
            pass


def parse_classdecl(cursor, className, classMembers, baseClassName):
    if cursor.spelling == className:
        for children in cursor.get_children():
            try:
                if children.kind == clang.cindex.CursorKind.FIELD_DECL:
                    parse_fielddecl(children, className, classMembers)
                elif children.kind == clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
                    base_class = children.get_definition()
                    for base_children in base_class.get_children():
                        # print(base_children.displayname)
                        if base_children.displayname == "_cloneFrom(const Ogre::EmitterDefData * _Nonnull)":
                            baseClassName.append(base_class.spelling)
                            parse_baseclasses(base_class, baseClassName)
                            break
            except ValueError:
                pass


def parse_fielddecl(cursor, className, classMembers):
    cursortype = cursor.type
    if cursortype.kind == clang.cindex.TypeKind.TYPEDEF:
        cursortype = cursortype.get_canonical()

    size = (-1, )
    if cursortype.kind == clang.cindex.TypeKind.RECORD:
        # LibClang detects FastArray<T> as RECORD (e.g. PbsBakedTextureArray)
        # @hack Consider RECORD as vector-like type
        size = (0, )
    elif cursortype.kind == clang.cindex.TypeKind.CONSTANTARRAY:
        if cursortype.element_type.kind == clang.cindex.TypeKind.CONSTANTARRAY:
            # Bidimensional C-style array
            # @todo Add support for multidimensional C-style array
            size = (cursortype.element_count,
                    cursortype.element_type.element_count)
        else:
            # C-style array
            size = (cursortype.element_count, )

    classMembers.append((cursor.spelling, size))


FileHeader = u"""
// This file has been auto-generated by clone_particle_systems.py
// Please DO NOT manually edit this file. Any subsequent invocation of
// clone_particle_systems.py will overwrite your modifications.
"""

CallBaseFunctionCopy = u"    {baseClass}::_cloneFrom( _original );"

CloneCodeTemplateBody = u"""
//-----------------------------------------------------------------------------
void {className}::_cloneFrom( const {mostBaseClass} *_original )
{{
    OGRE_ASSERT_HIGH( dynamic_cast<const {className} *>( _original ) );
{baseFunctionCopy}
    const {className} *original = static_cast<const {className} *>( _original );
{membersCopyCode}
}}
"""

CloneCodeTemplateVariable = u"""    this->{varName} = original->{varName};
"""


def writeEmitterDefDataBody(className, classMembers, baseClassMembers):
    # Copy every variable member
    membersCopyCode = ''
    for member in classMembers:
        membersCopyCode += CloneCodeTemplateVariable.format(varName=member[0])
    for member in baseClassMembers:
        membersCopyCode += CloneCodeTemplateVariable.format(varName=member[0])

    # Remove last newline
    membersCopyCode = membersCopyCode[:-1]

    cppStr = CloneCodeTemplateBody.format(
        className=className, baseClass=className, mostBaseClass=className,
        baseFunctionCopy='', membersCopyCode=membersCopyCode)

    return cppStr


def writeCppSrcCloneBody(className, classMembers, baseClassNames):
    # Copy every variable member
    membersCopyCode = ''
    for member in classMembers:
        membersCopyCode += CloneCodeTemplateVariable.format(varName=member[0])

    # Remove last newline
    membersCopyCode = membersCopyCode[:-1]

    # Call base function (if any)
    baseFunctionCopy = ''
    if (len(baseClassNames) == 0):
        baseClassNames = [className]
    else:
        baseFunctionCopy = CallBaseFunctionCopy.format(
            baseClass=baseClassNames[0])

    # Semi-final output
    cppStr = CloneCodeTemplateBody.format(
        className=className, baseClass=baseClassNames[0], mostBaseClass=baseClassNames[-1],
        baseFunctionCopy=baseFunctionCopy, membersCopyCode=membersCopyCode)

    return cppStr


classesToParse = ['AreaEmitter2', 'BoxEmitter2', 'CylinderEmitter2',
                  'EllipsoidEmitter2', 'HollowEllipsoidEmitter2', 'PointEmitter2', 'RingEmitter2']


def writeFileIfChanged(newFile, fullPath):
    try:
        oldFile = io.open(fullPath, 'r', encoding='utf-8', newline="\n")
    except IOError:
        oldFile = None

    newFile.seek(0, io.SEEK_SET)

    # Raw compare.
    if not oldFile or oldFile.read() != newFile.read():
        if oldFile:
            oldFile.seek(0, io.SEEK_SET)
        newFile.seek(0, io.SEEK_SET)
        print("File " + fullPath + " is outdated. Overwriting...")
        if oldFile:
            oldFile.close()
        oldFile = io.open(fullPath, 'w', encoding='utf-8', newline="\n")
        oldFile.write(newFile.read())
        oldFile.close()
    else:
        print("File " + fullPath + " is up to date.")
    newFile.close()
    return


def parseClass(className, clangArgs):
    clangIndex = clang.cindex.Index.create()
    headerFile = "../../PlugIns/ParticleFX2/include/Ogre{className}.h".format(
        className=className)
    print("Parsing " + headerFile)
    translationunit = clangIndex.parse(headerFile, clangArgs)
    for diag in translationunit.diagnostics:
        print(diag)

    classMembers = []
    baseClassNames = []
    parse_any(translationunit.cursor, className,
              classMembers, baseClassNames)

    # Sort classMembers for prettyprint source code
    classMembers.sort(key=lambda x: x[1][0])

    if len(classMembers) > 0:
        cppStr = writeCppSrcCloneBody(className, classMembers, baseClassNames)
    else:
        cppStr = ''

    return cppStr


# The class EmitterDefData is a special case for 2 reasons:
#   1. EmitterDefData definition goes into OgreMain (the rest go into ParticleFX2 plugin)
#   2. ParticleEmitter must be cloned but we don't want to expose _cloneFrom() in that
#      class since it's a legacy class, hence the copy must be done by EmitterDefData
def parseBaseClass(cursor):
    emitterDefDataClass = []
    particleEmitterClass = []
    baseClassNames = []
    parse_any(cursor, 'EmitterDefData', emitterDefDataClass, baseClassNames)
    parse_any(cursor, 'ParticleEmitter', particleEmitterClass, baseClassNames)

    # Sort classMembers for prettyprint source code
    emitterDefDataClass.sort(key=lambda x: x[1][0])
    particleEmitterClass.sort(key=lambda x: x[1][0])

    # Open a file in memory
    newFile = io.StringIO(newline="\n")
    # Write the full body
    newFile.write(writeEmitterDefDataBody('EmitterDefData',
                                          emitterDefDataClass, particleEmitterClass))
    writeFileIfChanged(
        newFile, "../../OgreMain/src/ParticleSystem/OgreEmitter2Clone.autogen.h")


def main():
    argparser = argparse.ArgumentParser(
        description="Auto-generate \"cloneImpl\" source code")
    argparser.add_argument(
        "HEADER", nargs="+", help='HLMS datablock class header for which the "cloneImpl" source code has to be generated')
    argparser.add_argument("-I", "--include-directory", action="append",
                           help="add directory to include search path")
    argparser.add_argument(
        "-l", "--library", help="set LibClang shared library (libclang.so or libclang.dll)")

    args = argparser.parse_args()

    setup_clang(args.library)

    index = clang.cindex.Index.create()
    indexargs = ["-x", "c++"]

    if args.include_directory:
        for includedirectory in args.include_directory:
            indexargs += ["-I", includedirectory]

    # Open a file in memory
    cppStr = io.StringIO(newline="\n")
    cppStr.write(FileHeader)

    # The base class is two classes parsed into one, in OgreMain core. It's a special case.
    parseBaseClass(index.parse(
        '../../OgreMain/include/ParticleSystem/OgreEmitter2.h', indexargs).cursor)

    # Now do all emitters in multiple threads then join
    # Add all includes first.
    for className in classesToParse:
        cppStr.write("#include \"Ogre{className}.h\"\n".format(
            className=className))

    cppStr.write("using namespace Ogre;")

    # Run in threads
    pool = ThreadPool()
    result = pool.map(
        partial(parseClass, clangArgs=indexargs),  classesToParse)
    for r in result:
        cppStr.write(r)

    writeFileIfChanged(
        cppStr, "../../PlugIns/ParticleFX2/src/OgreAllEmittersClone.autogen.cpp")
    # print(cppStr.read())


if __name__ == "__main__":
    main()
