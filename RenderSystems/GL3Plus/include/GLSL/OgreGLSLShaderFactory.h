/*
  -----------------------------------------------------------------------------
  This source file is part of OGRE-Next
  (Object-oriented Graphics Rendering Engine)
  For the latest info, see http://www.ogre3d.org/

  Copyright (c) 2000-2014 Torus Knot Software Ltd

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
  -----------------------------------------------------------------------------
*/

#ifndef __GLSLShaderFactory_H__
#define __GLSLShaderFactory_H__

#include "OgreGLSLExtSupport.h"

#include "OgreHighLevelGpuProgramManager.h"

namespace Ogre
{
    /** Factory class for GLSL shaders.
     */
    class _OgreGL3PlusExport GLSLShaderFactory final : public HighLevelGpuProgramFactory
    {
    protected:
        static String mLanguageName;

    public:
        GLSLShaderFactory( const GL3PlusSupport &support );
        ~GLSLShaderFactory() override;
        /// Get the name of the language this factory creates shaders for.
        const String &getLanguage() const override;

        /// Create an instance of GLSLProgram.
        HighLevelGpuProgram *create( ResourceManager *creator, const String &name, ResourceHandle handle,
                                     const String &group, bool isManual,
                                     ManualResourceLoader *loader ) override;

        void destroy( HighLevelGpuProgram *prog ) override;

    private:
        static GLSLMonolithicProgramManager *mMonolithicProgramManager;
    };
}  // namespace Ogre

#endif  // __GLSLShaderFactory_H__
