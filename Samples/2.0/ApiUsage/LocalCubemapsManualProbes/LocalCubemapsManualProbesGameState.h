
#ifndef _Demo_LocalCubemapsManualProbesGameState_H_
#define _Demo_LocalCubemapsManualProbesGameState_H_

#include "OgrePrerequisites.h"
#include "TutorialGameState.h"

namespace Ogre
{
    class ParallaxCorrectedCubemap;
    class ParallaxCorrectedCubemapAuto;
    class ParallaxCorrectedCubemapBase;
    class HlmsPbsDatablock;
}  // namespace Ogre

namespace Demo
{
    class LocalCubemapsManualProbesGameState : public TutorialGameState
    {
        Ogre::SceneNode *mLightNodes[3];

        Ogre::ParallaxCorrectedCubemapBase *mParallaxCorrectedCubemap;
        Ogre::ParallaxCorrectedCubemapAuto *mParallaxCorrectedCubemapAuto;
        Ogre::ParallaxCorrectedCubemap *mParallaxCorrectedCubemapOrig;
        Ogre::HlmsPbsDatablock *mMaterials[4 * 4];
        bool mPerPixelReflections;
        /// True if we were using manual probes before mPerPixelReflections became true
        bool mWasManualProbe;

        virtual void generateDebugText( float timeSinceLast, Ogre::String &outText );

        void setupParallaxCorrectCubemaps();

    public:
        LocalCubemapsManualProbesGameState( const Ogre::String &helpDescription );

        virtual void createScene01();
        virtual void destroyScene();

        virtual void update( float timeSinceLast );

        virtual void keyReleased( const SDL_KeyboardEvent &arg );
    };
}  // namespace Demo

#endif
