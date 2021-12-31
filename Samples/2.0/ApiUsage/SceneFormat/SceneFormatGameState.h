
#ifndef _Demo_SceneFormatGameState_H_
#define _Demo_SceneFormatGameState_H_

#include "OgrePrerequisites.h"
#include "TutorialGameState.h"

namespace Ogre
{
    class InstantRadiosity;
    class IrradianceVolume;
    class ParallaxCorrectedCubemap;
}  // namespace Ogre

namespace Demo
{
    class SceneFormatGameState : public TutorialGameState
    {
        Ogre::String mFullpathToFile;
        Ogre::InstantRadiosity *mInstantRadiosity;
        Ogre::IrradianceVolume *mIrradianceVolume;
        Ogre::ParallaxCorrectedCubemap *mParallaxCorrectedCubemap;

        virtual void generateDebugText( float timeSinceLast, Ogre::String &outText );

    public:
        void resetScene();
        void setupParallaxCorrectCubemaps();
        void destroyInstantRadiosity();
        void destroyParallaxCorrectCubemaps();

        Ogre::TextureGpu *createRawDecalDiffuseTex();
        void generateScene();
        void exportScene();
        void importScene();

    public:
        SceneFormatGameState( const Ogre::String &helpDescription );

        virtual void createScene01();
        virtual void destroyScene();

        virtual void keyReleased( const SDL_KeyboardEvent &arg );
    };
}  // namespace Demo

#endif
