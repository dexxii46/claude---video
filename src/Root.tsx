import {Composition} from 'remotion';
import {BlackIce} from './BlackIce';
import {TOTAL} from './words';
import {FPS, H, W} from './theme';

export const Root: React.FC = () => (
	<Composition
		id="BlackIce"
		component={BlackIce}
		durationInFrames={TOTAL}
		fps={FPS}
		width={W}
		height={H}
		defaultProps={{showSafeZone: false}}
	/>
);
