import {Composition} from 'remotion';
import {BlackIce} from './BlackIce';
import {TOTAL} from './words';
import {BASE_FPS, FPS, H, W} from './theme';

export const Root: React.FC = () => (
	<>
	<Composition
		id="BlackIce"
		component={BlackIce}
		durationInFrames={TOTAL * (FPS / BASE_FPS)}
		fps={FPS}
		width={W}
		height={H}
		defaultProps={{showSafeZone: false}}
	/>
	</>
);
