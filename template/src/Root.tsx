import React from 'react';
import {Composition} from 'remotion';
import {ReelCutaways} from './ReelCutaways';
import mapping from '../mapping.json';

export const Root: React.FC = () => (
	<Composition
		id="ReelCutaways"
		component={ReelCutaways}
		durationInFrames={mapping.durationInFrames}
		width={mapping.width}
		height={mapping.height}
		fps={mapping.fps}
	/>
);
