import {loadFont} from '@remotion/fonts';
import {staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

export const anton = 'Anton';
export const mont = 'Montserrat';

loadFont({family: anton, url: staticFile('fonts/Anton.woff2'), weight: '400'});
loadFont({family: mont, url: staticFile('fonts/Montserrat.woff2'), weight: '100 900'});

export const FPS = 60;
// All animation timings are authored in 30fps "beats"; this maps any render fps onto them.
export const BASE_FPS = 30;
export const useF = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return frame / (fps / BASE_FPS);
};
export const useR = () => useVideoConfig().fps / BASE_FPS;
export const W = 1080;
export const H = 1920;

// TikTok + IG Reels safe zone (union of both UIs, 1080x1920)
export const SAFE = {top: 250, bottom: 1500, left: 60, right: 910};

// Product sits roughly y 570–1410 in this footage. Graphics live above or below it.
export const ZONE_TOP = {y: 270, h: 290}; // car bonnet area
export const ZONE_LOW = {y: 1400, h: 100}; // forearm / ground area, above platform UI

export const C = {
	ice: '#9BE8FF',
	iceDeep: '#2FB8FF',
	white: '#FFFFFF',
	black: '#05080C',
	yellow: '#FFD21F',
	red: '#FF2D46',
};
