import React from 'react';
import { EffectComposer, Bloom } from '@react-three/postprocessing';

function PostProcessing() {
  return (
    <EffectComposer>
      <Bloom
        intensity={1.2}
        luminanceThreshold={0.4}
        luminanceSmoothing={0.85}
        mipmapBlur
      />
    </EffectComposer>
  );
}

export default PostProcessing;
